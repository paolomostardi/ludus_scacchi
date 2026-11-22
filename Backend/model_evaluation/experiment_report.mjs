import { createServer, request as httpRequest } from 'node:http';
import { request as httpsRequest } from 'node:https';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

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
const datasetLabels = new Map([
  ['lichess-bitboards-2013-01', 'Jan 2013'],
  ['ludus-1500-2017-04-general-train-v1', 'April general'],
  ['ludus-1500-2017-04-general-eval-v1', 'April general'],
  ['ludus-1500-2017-04-endgame-train-v1', 'April endgame'],
  ['ludus-1500-2017-04-endgame-eval-v1', 'April endgame'],
  ['ludus-1500-2017-04-endgame-train-v2', 'Endgame v2'],
  ['ludus-1500-2017-04-endgame-eval-v2', 'Endgame v2'],
  ['ludus-2000-general-train-v1', 'May 2000 training'],
  ['ludus-2000-general-eval-v1', 'May 2000'],
  ['ludus-2013-01-overlap-clean-eval-v1', 'Jan 2013 clean'],
  [simpleCatalog, 'Simple positions'],
]);
const shortArchitecture = name => {
  const resnet = /^(?:Ludus[-_])?(?:source[-_])?resnet[-_](\d+)x(\d+)$/i.exec(name ?? '');
  return resnet ? 'ResNet ' + resnet[1] + '×' + resnet[2] : displayModelName(name);
};
const shortRun = name => {
  const label = displayModelName(name)
    .replace(/^(?:Ludus[-_])?resnet[-_]\d+x\d+[ _-]+/i, '')
    .replace(/\bfine-tune on (\S+)/i, (text, dataset) =>
      datasetLabels.has(dataset) ? 'Fine-tune ' + datasetLabels.get(dataset) : text)
    .replace(/\(LR ([^,]+), epoch (\d+)\)/gi, '· LR $1 · E$2');
  return label.length > 42 ? label.slice(0, 41) + '…' : label;
};
const withTitle = (label, title) => title == null ? escape(label)
  : '<span title="' + escape(title) + '">' + escape(label) + '</span>';

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
    version = run.tags['evaluation_dataset_version.' + suffix] || version;
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
  const runFields = [
    ['Optimizer', 'optimizer'], ['Momentum', 'momentum'], ['Learning rate', 'learning_rate'],
    ['LR schedule', 'lr_schedule'], ['Weight decay', 'weight_decay'], ['Batch size', 'batch_size'],
    ['Epochs', 'epochs'], ['Seed', 'seed'], ['Starting run', 'initialization_run_id'],
  ];
  const identityHeaders = [{ label: 'ID', title: 'Sort by ID', sortNumeric: true }, 'Run Date', 'Run', 'Architecture'];
  const detailHeaders = ['Total parameters', ...runFields.map(([label]) => label)];
  const datasetHeader = (name, sortAccuracy = false) => ({
    label: datasetLabels.get(name) ?? name, title: name, sortAccuracy,
  });
  const headers = [...identityHeaders, ...evaluationColumns.map(name => datasetHeader(name, true)),
    ...trainingColumns.map(name => datasetHeader(name)), ...detailHeaders];
  const groups = [['Run', identityHeaders.length], ['Evaluation datasets', evaluationColumns.length],
    ['Training datasets', trainingColumns.length], ['Training settings', detailHeaders.length]];
  const rows = runs.flatMap(run => {
    const p = run.params;
    const legacyOptimizer = /^(SGD) with momentum (\d+(?:\.\d+)?)$/i.exec(p.optimizer ?? '');
    const runResults = byTrainingRun.get(run.id);
    if (runIds.has(run.tags['mlflow.parentRunId']) && !p.training_dataset && !runResults) return [];
    const architecture = p.architecture_variant || p.model_name || p.architecture_name || p.model_factory;
    const total = p.total_parameters ?? p.total_params ?? p.model_parameter_count ?? totals.get(architecture);
    const trainedOn = new Set(trainingNames(run));
    const date = run.startTime == null ? undefined : new Date(Number(run.startTime));
    const identityCells = [
      escape(date && Number.isFinite(date.getTime()) ? runDate.format(date) : undefined),
      withTitle(shortRun(run.name), run.name),
      withTitle(shortArchitecture(architecture), architecture),
    ];
    const detailCells = [
      number(total),
      ...runFields.map(([, key]) => {
        if (key === 'optimizer' && legacyOptimizer) return escape(legacyOptimizer[1]);
        const value = p[key] ?? run.tags[key] ?? (key === 'momentum' ? legacyOptimizer?.[2] : undefined);
        if (key === 'learning_rate' && value != null && String(value).trim() !== '') {
          const rate = Number(value);
          if (Number.isFinite(rate)) {
            const label = rate !== 0 && Math.abs(rate) < 0.0001
              ? rate.toExponential(3).replace(/\.?0+e/, 'e')
              : rate.toFixed(4).replace(/\.?0+$/, '');
            return withTitle(label, value);
          }
        }
        return key === 'initialization_run_id' && /^[a-f0-9]{32}$/i.test(value ?? '')
          ? withTitle(value.slice(0, 8) + '…', value) : escape(value);
      }),
    ];
    const trainingCells = trainingColumns.map(name => trainedOn.size ? String(trainedOn.has(name))
      : '<span title="Training datasets unrecorded">—</span>');
    const evaluationsByName = runResults || new Map();
    const metricCells = evaluationColumns.map(name => {
      const result = evaluationsByName.get(name);
      if (!result) return '<span title="Not evaluated">—</span>';
      const score = result.metrics.accuracy;
      return '<span title="Top-1 accuracy"' + (Number.isFinite(score) ? ' data-top1="' + score + '"' : '')
        + '>Top-1 ' + percent(score)
        + '</span><br><span title="Top-3 accuracy">Top-3 ' + percent(result.metrics.top3_accuracy) + '</span>';
    });
    return [{ runId: run.id, cells: [...identityCells, ...metricCells, ...trainingCells, ...detailCells] }];
  });
  const orderedRows = rows.sort((left, right) => {
    const leftRun = runs.find(run => run.id === left.runId);
    const rightRun = runs.find(run => run.id === right.runId);
    return Number(leftRun?.startTime ?? 0) - Number(rightRun?.startTime ?? 0)
      || left.runId.localeCompare(right.runId);
  });
  return {headers, rows: orderedRows.map(({ runId, cells }, index) => ({
    runId, cells: [String(index + 1), ...cells],
  })), groups};
}

function table(headers, rows, groups = []) {
  const groupHeader = groups.filter(([, count]) => count > 0).map(([label, count]) =>
    '<th scope="colgroup" colspan="' + count + '">' + escape(label) + '</th>').join('');
  const columnHeaders = headers.map(header => {
    const { label, title, sortAccuracy, sortNumeric } = typeof header === 'string' ? { label: header } : header;
    const content = sortAccuracy || sortNumeric
      ? '<button type="button" data-sort-accuracy title="' + escape(sortNumeric ? title : title + ' · Sort by Top-1 accuracy')
        + '">' + escape(label) + '</button>'
      : withTitle(label, title);
    return '<th scope="col">' + content + '</th>';
  }).join('');
  return '<table><thead>' + (groupHeader ? '<tr>' + groupHeader + '</tr>' : '') + '<tr>' + columnHeaders +
    '</tr></thead><tbody>' + (rows.length ? rows.map(row =>
      '<tr>' + (row.cells || row).map((cell, index) =>
        (index === 0 && row.runId ? '<td data-run-id="' + escape(row.runId) + '">' : '<td>')
        + cell + '</td>').join('') + '</tr>').join('')
      : '<tr><td colspan="' + headers.length + '">No records found.</td></tr>') + '</tbody></table>';
}

function architectureRows(runs) {
  const architectures = new Map();
  for (const run of runs) {
    if (run.tags['mlflow.parentRunId'] && !run.params.training_dataset) continue;
    const p = run.params;
    const architecture = p.architecture_variant || p.model_name || p.architecture_name || p.model_factory;
    if (!architecture) continue;

    const resnet = /^(?:Ludus-)?source[-_]resnet[-_](\d+)x(\d+)(?:[-_]dense(\d+))?$/i.exec(architecture);
    const denseUnits = resnet?.[3];
    const compact = architecture === 'model_testing_mlflow';
    const blocks = resnet?.[1] || (compact ? 1 : p.residual_blocks);
    const filters = resnet?.[2] || p.conv_filters;
    const upsample = p.upsample_factor;
    const name = resnet ? 'ResNet ' + blocks + '×' + filters + (denseUnits ? ' Dense ' + denseUnits : '')
      : compact && filters && upsample ? 'Compact CNN (' + filters + ' filters, ' + upsample + '× upsampling)'
        : displayModelName(architecture);
    const key = JSON.stringify([name, p.board_encoding_id, p.board_layout, compact ? upsample : undefined]);
    const total = p.total_parameters ?? p.total_params ?? p.model_parameter_count
      ?? (resnet && !denseUnits ? totals.get('source_resnet_' + blocks + 'x' + filters) : undefined)
      ?? (compact && Number(filters) === 12 ? 12304 : undefined);
    const shape = p.input_shape ?? (resnet || compact ? '15 × 8 × 8 board planes' : undefined);
    const input = [shape, p.board_layout, p.board_encoding_id].filter(Boolean).join(' · ') || undefined;
    const head = denseUnits ? '1 × 1 convolution plus dense correction (' + denseUnits + ' → 64); 64-way softmax'
      : resnet ? '1 × 1 convolution on the 8 × 8 board; 64-way softmax'
      : compact ? 'Global average pooling, dense layer, 64-way softmax' : p.head_type;
    const backbone = resnet ? '3 × 3 convolution; two 3 × 3 convolutions per residual block; batch normalization and ReLU'
      : compact ? 'Upsampling, 3 × 3 convolution, then one residual block with stride 2' : p.architecture_family;
    const output = resnet || compact ? 'Source square (64 classes)' : p.output_shape;
    const entry = [name, number(total), blocks, filters, denseUnits ? 2 : resnet ? 0 : compact ? 2 : undefined,
      input, backbone, head, output];
    const existing = architectures.get(key);
    architectures.set(key, existing ? existing.map((value, index) =>
      value == null || value === '—' ? entry[index] : value) : entry);
  }
  return [...architectures.values()].sort((left, right) => left[0].localeCompare(right[0]))
    .map(row => row.map(escape));
}

const sortScript = `
for (const button of document.querySelectorAll('[data-sort-accuracy]')) {
  button.addEventListener('click', () => {
    const header = button.closest('th');
    const table = header.closest('table');
    const column = header.cellIndex;
    const ascending = header.getAttribute('aria-sort') === 'descending';
    for (const sorted of table.querySelectorAll('th[aria-sort]')) sorted.removeAttribute('aria-sort');
    header.setAttribute('aria-sort', ascending ? 'ascending' : 'descending');

    const body = table.tBodies[0];
    const numeric = button.closest('th').cellIndex === 0;
    const score = row => numeric ? row.cells[column]?.textContent.trim()
      : row.cells[column]?.querySelector('[data-top1]')?.dataset.top1;
    const rows = [...body.rows].sort((left, right) => {
      const a = score(left);
      const b = score(right);
      if (a === undefined) return b === undefined ? 0 : 1;
      if (b === undefined) return -1;
      return ascending ? Number(a) - Number(b) : Number(b) - Number(a);
    });
    body.append(...rows);
  });
}
`;
const sortHash = createHash('sha256').update(sortScript).digest('base64');

function render(runs, markdown) {
  runs = runs.filter(run => run.tags.ludus_report !== 'exclude'
    && run.name !== 'first_model_smoke_test' && run.params.test_type !== 'pipeline_smoke');
  const inventoryRows = readInventory(markdown);
  const datasetNames = new Map(inventoryRows.map(({name}) => [nameKey(name), name]));
  const results = runs.flatMap(run => evaluations(run, datasetNames)).filter(result => result.name !== legacy);
  const datasets = datasetRows(inventoryRows, runs, results);
  const training = trainingRows(runs, results, datasets);
  const datasetHeaders = ['Dataset', 'Version', 'Data points', 'Content hash', 'Variation'];
  const architectureHeaders = ['Architecture', 'Parameters', 'Residual blocks', 'Stem filters', 'Dense layers', 'Input', 'Backbone', 'Prediction head', 'Output'];
  const datasetCells = ({ name, version, count, hash, note }) => [name, version, number(count), hash, note].map(escape);
  return '<!doctype html><html lang="en"><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1"><title>Ludus experiment report</title>' +
    '<style>body{font:15px/1.5 system-ui,sans-serif;margin:2rem auto;padding:0 1rem;max-width:90rem;color:#192126}' +
    'h1,h2{line-height:1.2}section{margin-bottom:2rem}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse}' +
    '.training-scroll table{width:max-content;min-width:100%;white-space:nowrap}' +
    'td,th{text-align:left;vertical-align:top;padding:.65rem;border-bottom:1px solid #ccd7da;overflow-wrap:anywhere}' +
    'th{background:#dae9f6}tbody tr:nth-child(odd){background:#eef6fd}tbody tr:nth-child(even){background:#fbfdff}' +
    'th button{font:inherit;color:inherit;text-align:left;background:none;border:0;padding:0;cursor:pointer;overflow-wrap:anywhere}' +
    'th button:after{content:" ↕"}th[aria-sort="ascending"] button:after{content:" ↑"}th[aria-sort="descending"] button:after{content:" ↓"}</style>' +
    '<h1>Ludus experiment report</h1><section><h2 id="training-runs">Training runs</h2><div class="scroll training-scroll" tabindex="0" role="region" aria-labelledby="training-runs">' +
    table(training.headers, training.rows, training.groups) +
    '</div></section><section><h2>Architectures</h2><div class="scroll">' +
    table(architectureHeaders, architectureRows(runs)) +
    '</div></section><section><h2>Datasets</h2><h3>Training datasets</h3><div class="scroll">' +
    table(datasetHeaders, datasets.training.map(datasetCells)) +
    '</div><h3>Evaluation datasets</h3><div class="scroll">' +
    table(datasetHeaders, datasets.evaluation.map(datasetCells)) + '</div></section>' +
    '<script>' + sortScript + '</script></html>';
}

if (!uri || !/^https?:\/\//i.test(uri)) {
  throw new Error('Set MLFLOW_TRACKING_URI to the HTTP(S) address of your tracking server.');
}

async function loadReport() {
  return render(...await Promise.all([loadRuns(), readFile(inventory, 'utf8')]));
}

if (process.argv.includes('--snapshot')) {
  process.stdout.write(await loadReport());
} else createServer(async (request, response) => {
  response.setHeader('Cache-Control', 'no-store');
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.setHeader('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-"
    + sortHash + "'; frame-ancestors 'none'");
  if (request.method !== 'GET' || request.url !== '/report') {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Use GET /report.\n');
    return;
  }
  try {
    const html = await loadReport();
    response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }).end(html);
  } catch {
    response.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' })
      .end('Could not generate the report. Check the MLflow connection and dataset inventory.\n');
  }
}).listen(port, '127.0.0.1', () => {
  console.log('Ludus report available at http://127.0.0.1:' + port + '/report');
});
