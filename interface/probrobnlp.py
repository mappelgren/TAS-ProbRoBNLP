from flask import Flask, render_template, request, redirect, url_for

import probRobScene
import numpy as np

app = Flask(__name__)

def generate_images(scenario_file):
   scenario = probRobScene.scenario_from_file(scenario_file)

   max_generations = 9
   rejections_per_scene = []
   for i in range(max_generations):
       print(f"Generation {i}")
       ex_world, used_its = scenario.generate(verbosity=2)
       rejections_per_scene.append(used_its)
       ex_world.show_3d(save_location=f"static/test{i}.png")
   #
   avg_rejections = np.average(rejections_per_scene)



# messages = [('Robot', 'Hello Bob, what are we doing today?'), 
# ('Bob', 'Put a table in the room'),
# ('Robot', 'Ok, how big is the table?'),
# ('Bob', '1.4 by 0.8 and 0.7 tall'),
# ('Robot', 'ok'),
# ('Bob', 'Put a blue tray on the table')]
messages = [('Robot', 'Hello, tell me what to do.')]

current_file = 'cupPour.prs'

generate_images(f"static/{current_file}")

images = [['test0.png', 'test1.png', 'test2.png'],
['test3.png', 'test4.png', 'test5.png'],
['test6.png', 'test7.png', 'test8.png']]


@app.route('/')
def render_chat():
   with open(f'static/{current_file}', 'r') as f:
      file_data = f.read()
   return render_template('chat_interface.html', messages = messages, images=images, file_data=file_data)


def reset():
   messsages = [('Robot', 'Hello, tell me what to do.')]

@app.route('/form', methods=['POST'])
def new_message():
   result = request.form
   message = result['message']
   messages.append(('Bob', message))

   response = process_message(message)

   messages.append(response)

   return redirect(url_for('render_chat'))

def process_message(message):
   if "hello" in message.lower():
      return ('Robot', 'Hello, beep boop')
   else:
      return ('Robot', "I'm not very smart yet so I don't know how to respond to that")




if __name__ == '__main__':
   app.run(debug = True)