import { createServer, request as httpRequest } from 'node:http';
import { request as httpsRequest } from 'node:https';
import { readFile } from 'node:fs/promises';

const inventory = new URL('../../docs/dataset_inventory.md', import.meta.url);
const uri = process.env.MLFLOW_TRACKING_URI?.replace(/\/+$/, '');
const experiment = process.env.LUDUS_MLFLOW_EXPERIMENT || 'ludus_cnn';
const port = Number(process.env.LUDUS_REPORT_PORT || 8765);
const legacy = 'eval-training-2013-chunk-9';
const simpleCatalog = 'Simple position catalog';
const nameKey = name => name.toLowerCase().replace(/[^a-z0-9_]+/g, '_');
const totals = new Map([
  ['source_resnet_4x64', 306497], ['Ludus-Source-ResNet-4x64', 306497],
  ['source_resnet_6x64', 455233], ['Ludus-Source-ResNet-6x64', 455233],
]);
const escape = value => String(value ?? '—').replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));
const fields = entries => Object.fromEntries((entries || []).map(({ key, value }) => [key, value]));
const slug = name => name.split('/').at(-1);
const displayModelName = name => name?.replace(/(^|[-_\s])source[-_\s]+/gi, '$1');

async function mlflow(path, body) {
  const headers = { Accept: 'application/json' };
  const { MLFLOW_TRACKING_TOKEN: token, MLFLOW_TRACKING_USERNAME: user,
    MLFLOW_TRACKING_PASSWORD: password } = process.env;
  if (token) headers.Authorization = 'Bearer ' + token;
  else if (user && password) headers.Authorization = 'Basic ' + Buffer.from(user + ':' + password).toString('base64');
  if (body) headers['Content-Type'] = 'application/json';
  if (process.env.LUDUS_MLFLOW_HOST) headers.Host = process.env.LUDUS_MLFLOW_HOST;
  const url = new URL(uri + '/api/2.0/mlflow/' + path);
  const request = url.protocol === 'https:' ? httpsRequest : httpRequest;
  return new Promise((resolve, reject) => {
    const pending = request(url, {
      method: body ? 'POST' : 'GET', headers, signal: AbortSignal.timeout(15000),
    }, async response => {
      try {
        if (response.statusCode !== 200) {
          response.resume();
          throw new Error('MLflow returned HTTP ' + response.statusCode);
        }
        let json = '';
        response.setEncoding('utf8');
        for await (const chunk of response) json += chunk;
        resolve(JSON.parse(json));
      } catch (error) {
        reject(error);
      }
    });
    pending.on('error', reject);
    pending.end(body ? JSON.stringify(body) : undefined);
  });
}

async function loadRuns() {
  const query = new URLSearchParams({ experiment_name: experiment });
  const result = await mlflow('experiments/get-by-name?' + query);
  const runs = [];
  let pageToken;
  do {
    const page = await mlflow('runs/search', {
      experiment_ids: [result.experiment.experiment_id],
      max_results: 500,
      page_token: pageToken,
    });
    runs.push(...(page.runs || []));
    pageToken = page.next_page_token;
  } while (pageToken);
  return runs.map(({ info, data, inputs }) => ({
    id: info.run_id,
    name: info.run_name || fields(data?.tags)['mlflow.runName'] || info.run_id,
    status: info.status,
    startTime: info.start_time,
    params: fields(data?.params),
    tags: fields(data?.tags),
    metrics: fields(data?.metrics),
    inputs: inputs?.dataset_inputs || [],
  }));
}

function evaluations(run, datasetNames) {
  const groups = new Map();

  for (const [key, value] of Object.entries(run.metrics)) {
    const metricKey = key.replace(/^smoke_(sample|simple)_(accuracy|loss)$/, '$2_smoke_$1');
    const match = /^(top3_accuracy|accuracy|loss|sample_count)_(.+)$/.exec(metricKey);
    if (!match) continue;
    const [, metric, suffix] = match;
    if (suffix === 'simple' || /^simple_v2_|^legacy_eight_repaired(?:_|$)|^2013[-_]01$/.test(suffix)) continue;
    if (!groups.has(suffix)) groups.set(suffix, {});
    groups.get(suffix)[metric] = value;
  }
  return Array.from(groups, ([suffix, metrics]) => {
    let name = suffix;
    let version;
    let hash;
    const oldInput = run.tags.evaluation_dataset || run.params.evaluation_dataset;
    const input = run.tags['evaluation_dataset.' + suffix]
      || (oldInput && (suffix === 'general' || nameKey(slug(oldInput)) === suffix) ? oldInput : undefined);
    name = input ? slug(input) : datasetNames.get(nameKey(suffix)) || suffix;
    if (input && input === oldInput) {
      version = run.tags.evaluation_dataset_version || run.params.evaluation_dataset_version;
    }
    if (suffix === 'simple_v2') {
      name = simpleCatalog;
      version = run.tags.simple_v2_version || run.params.simple_v2_version;
      hash = run.tags.simple_v2_sha256 || run.params.simple_v2_sha256;
    }
    return { name, version, hash, metrics, run };
  });
}

function trainingDatasets(run) {
  const recorded = run.params.training_dataset_sequence;
  if (recorded) {
    try {
      const sequence = JSON.parse(recorded);
      if (Array.isArray(sequence) && sequence.length && sequence.every(name => typeof name === 'string' && name.trim())) {
        return { sequence };
      }
    } catch {
      // Older runs can still expose individual dataset inputs.
    }
  }
  const name = run.params.training_dataset;
  const names = new Set(name ? [name + (run.params.training_dataset_version ? ' · v' + run.params.training_dataset_version : '')] : []);
  for (const input of run.inputs) {
    const datasetName = input.dataset?.name;
    if (datasetName && (!name || slug(datasetName) !== slug(name)) && (input.tags || []).some(tag =>
      tag.key === 'mlflow.data.context' && tag.value === 'training')) {
      names.add(datasetName);
    }
  }
  return { names: [...names] };
}

function readInventory(markdown) {
  const row = /^\| `([^|]+?)` \| (\d+) \| ([^|]+?) \| ([^|]+?) \|/gm;
  return Array.from(markdown.matchAll(row), ([, name, version, count, note]) => ({
    name, version, count: count === '—' ? undefined : Number(count.replaceAll(',', '')), note,
  }));
}

function trainingNames(run) {
  const { sequence, names } = trainingDatasets(run);
  return (sequence || names).map(name => slug(name.split(' · v')[0]));
}

function datasetRows(inventoryRows, runs, results) {
  const rows = new Map();
  const training = new Set(runs.flatMap(trainingNames));
  const evaluation = new Set(results.map(result => result.name));
  for (const entry of inventoryRows) {
    if (/-train-v\d+$/.test(entry.name)) training.add(entry.name);
    if (/-eval-v\d+$/.test(entry.name)) evaluation.add(entry.name);
    if (training.has(entry.name) || evaluation.has(entry.name)) rows.set(entry.name, entry);
  }
  for (const result of results) {
    const existing = rows.get(result.name);
    if (result.name === simpleCatalog && existing?.count != null) continue;
    if (existing && !result.hash && (!result.version || result.version === existing.version)) continue;
    const key = existing && result.name !== simpleCatalog
      ? JSON.stringify([result.name, result.version, result.hash]) : result.name;
    rows.set(key, {
      name: result.name, version: result.version, hash: result.hash,
      count: result.name === simpleCatalog ? result.metrics.sample_count : undefined,
      note: 'Evaluation input recorded in MLflow.',
    });
  }
  for (const name of training) {
    if (!rows.has(name)) rows.set(name, {name, note: 'Training input recorded in MLflow.'});
  }
  const ordered = [...rows.values()].sort((a, b) => a.name.localeCompare(b.name));
  return {
    training: ordered.filter(row => training.has(row.name) && row.name !== simpleCatalog),
    evaluation: ordered.filter(row => evaluation.has(row.name)),
  };
}

const percent = value => Number.isFinite(value) ? (100 * value).toFixed(2) + '%' : '—';
const number = value => value != null && value !== '' && Number.isFinite(Number(value))
  ? Number(value).toLocaleString('en-US', { maximumFractionDigits: 4 }) : '—';


const runDate = new Intl.DateTimeFormat('sv-SE', {
  timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit', day: '2-digit',
});

function trainingRows(runs, results, datasets) {
  const runIds = new Set(runs.map(run => run.id));
  const byTrainingRun = new Map();
  for (const result of results) {
    const parent = result.run.tags['mlflow.parentRunId'];
    const owner = runIds.has(parent) ? parent : result.run.id;
    if (!byTrainingRun.has(owner)) byTrainingRun.set(owner, new Map());
    const previous = byTrainingRun.get(owner).get(result.name);
    if (!previous || (result.metrics.sample_count || 0) > (previous.metrics.sample_count || 0)) {
      byTrainingRun.get(owner).set(result.name, result);
    }
  }
  const trainingColumns = datasets.training.map(dataset => dataset.name);
  const evaluationColumns = [...new Set(datasets.evaluation.map(dataset => dataset.name))];
  const headers = ['Run date', 'Run', 'Architecture', 'Total parameters', ...trainingColumns, ...evaluationColumns];
  const groups = [['Run details', 4], ['Training datasets', trainingColumns.length],
    ['Evaluation datasets', evaluationColumns.length]];
  const rows = runs.flatMap(run => {
    const p = run.params;
    const runResults = byTrainingRun.get(run.id);
    if (runIds.has(run.tags['mlflow.parentRunId']) && !p.training_dataset && !runResults) return [];
    const architecture = p.architecture_variant || p.model_name || p.architecture_name || p.model_factory;
    const total = p.total_parameters ?? p.total_params ?? p.model_parameter_count ?? totals.get(architecture);
    const trainedOn = new Set(trainingNames(run));
    const date = run.startTime == null ? undefined : new Date(Number(run.startTime));
    const cells = [
      escape(date && Number.isFinite(date.getTime()) ? runDate.format(date) : undefined),
      escape(displayModelName(run.name)),
      escape(displayModelName(architecture)), number(total),
      ...trainingColumns.map(name => trainedOn.size ? String(trainedOn.has(name))
        : '<span title="Training datasets unrecorded">—</span>'),
    ];
    const evaluationsByName = runResults || new Map();
    const metricCells = evaluationColumns.map(name => {
      const result = evaluationsByName.get(name);
      if (!result) return '<span title="Not evaluated">—</span>';
      return '<span title="Top-1 accuracy">Top-1 ' + percent(result.metrics.accuracy)
        + '</span><br><span title="Top-3 accuracy">Top-3 ' + percent(result.metrics.top3_accuracy) + '</span>';
    });
    return [[...cells, ...metricCells]];
  });
  return {headers, rows, groups};
}

function table(headers, rows, groups = []) {
  const groupHeader = groups.filter(([, count]) => count > 0).map(([label, count]) =>
    '<th scope="colgroup" colspan="' + count + '">' + escape(label) + '</th>').join('');
  return '<table><thead>' + (groupHeader ? '<tr>' + groupHeader + '</tr>' : '') + '<tr>' + headers.map(value => '<th scope="col">' + escape(value) + '</th>').join('') +
    '</tr></thead><tbody>' + (rows.length ? rows.map(row =>
      '<tr>' + row.map(cell => '<td>' + cell + '</td>').join('') + '</tr>').join('')
      : '<tr><td colspan="' + headers.length + '">No records found.</td></tr>') + '</tbody></table>';
}

function render(runs, markdown) {
  runs = runs.filter(run => run.tags.ludus_report !== 'exclude'
    && run.name !== 'first_model_smoke_test' && run.params.test_type !== 'pipeline_smoke');
  const inventoryRows = readInventory(markdown);
  const datasetNames = new Map(inventoryRows.map(({name}) => [nameKey(name), name]));
  const results = runs.flatMap(run => evaluations(run, datasetNames)).filter(result => result.name !== legacy);
  const datasets = datasetRows(inventoryRows, runs, results);
  const training = trainingRows(runs, results, datasets);
  const datasetHeaders = ['Dataset', 'Version', 'Data points', 'Content hash', 'Variation'];
  const datasetCells = ({ name, version, count, hash, note }) => [name, version, number(count), hash, note].map(escape);
  return '<!doctype html><html lang="en"><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1"><title>Ludus experiment report</title>' +
    '<style>body{font:15px/1.5 system-ui,sans-serif;margin:2rem auto;padding:0 1rem;max-width:90rem;color:#192126}' +
    'h1,h2{line-height:1.2}section{margin-bottom:2rem}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse}' +
    'td,th{text-align:left;vertical-align:top;padding:.65rem;border-bottom:1px solid #ccd7da;overflow-wrap:anywhere}' +
    'th{background:#dae9f6}tbody tr:nth-child(odd){background:#eef6fd}tbody tr:nth-child(even){background:#fbfdff}</style>' +
    '<h1>Ludus experiment report</h1><section><h2>Training runs</h2><div class="scroll">' +
    table(training.headers, training.rows, training.groups) +
    '</div></section><section><h2>Datasets</h2><h3>Training datasets</h3><div class="scroll">' +
    table(datasetHeaders, datasets.training.map(datasetCells)) +
    '</div><h3>Evaluation datasets</h3><div class="scroll">' +
    table(datasetHeaders, datasets.evaluation.map(datasetCells)) + '</div></section></html>';
}

if (!uri || !/^https?:\/\//i.test(uri)) {
  throw new Error('Set MLFLOW_TRACKING_URI to the HTTP(S) address of your tracking server.');
}

createServer(async (request, response) => {
  response.setHeader('Cache-Control', 'no-store');
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.setHeader('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'");
  if (request.method !== 'GET' || request.url !== '/report') {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Use GET /report.\n');
    return;
  }
  try {
    const [runs, markdown] = await Promise.all([loadRuns(), readFile(inventory, 'utf8')]);
    const html = render(runs, markdown);
    response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }).end(html);
  } catch {
    response.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' })
      .end('Could not generate the report. Check the MLflow connection and dataset inventory.\n');
  }
}).listen(port, '127.0.0.1', () => {
  console.log('Ludus report available at http://127.0.0.1:' + port + '/report');
});
