import pcg_benchmark
from pcg_benchmark.probs.binary.problem import BinaryProblem

env_params = {
    'width': 16,
    'height': 16,
    'path': 100
    }
env_name = 'binary-w16-h16-p100'
pcg_benchmark.register(env_name, BinaryProblem, env_params)
# env = pcg_benchmark.make('binary-v0')
env = pcg_benchmark.make(env_name)
# generate 100 random content from the content_space
contents = [env.content_space.sample() for _ in range(10)]

# geberate 100 random control parameters from the control_space
controls = [env.control_space.sample() for _ in range(10)]

# evaluate contents and controls from quality, diversity, controlability metrics
# quality is the percentage of the 100 levels that has passed the quality criteria
# diversity is the percentage of the 100 levels that are different from each other
# controlability is the percentage of the 100 levels that fits with the controls parameters
# details is a dictionary with "quality", "diversity", and "controlability" keys that have float array of 100 numbers between 0 and 1 which represents how close to solve the problem
# infos is an array of dictionaries that contain details about each content
quality, diversity, controlability, details, infos = env.evaluate(contents, controls)

# generate images for each content
imgs = env.render(contents, infos=infos) 
# save the images to a folder
for i, img in enumerate(imgs):
    img.save(f'content_{i}.png')