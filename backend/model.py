import tensorflow as tf

# Set the logging verbosity level
tf.get_logger().setLevel('INFO')

# Load the SavedModel
model_dir = r"C:\Users\paolo\Downloads\my_model"
options = tf.saved_model.LoadOptions(experimental_io_device='/job:localhost')
model = tf.saved_model.load(model_dir, tags=["serve"], options=options)





