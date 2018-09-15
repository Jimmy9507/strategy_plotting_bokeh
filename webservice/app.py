import os

from flask import Flask, jsonify
from flask_pymongo import PyMongo

from webservice.config import DevelopConfig, ProductionConfig

the_app = Flask(__name__)

plots_list = ['plot_1', 'plot_2', 'plot_3', 'plot_4', 'plot_8', 'plot_9', 'plot_10', 'plot_11',
              'plot_17', 'plot_18', 'plot_20', 'plot_21', 'plot_25', 'plot_26', 'plot_27',
              'plot_28', 'plot_29', 'plot_30', 'plot_31', 'plot_32']

env = os.getenv('RQ_ENV', 'internal')
if env == 'internal':
    the_app.config.from_object(DevelopConfig)
elif env == 'production':
    the_app.config.from_object(ProductionConfig)

the_app.config.from_envvar('RQANALYSIS_CONF', silent=True)

mongo = PyMongo(the_app)


@the_app.route('/pyfoliod/<int:run_id>', methods=['GET'])
def get_plots(run_id):
    plot_in_db = mongo.db.pyloliod.find_one({'run_id': run_id})
    if plot_in_db is None:
        taks_state = mongo.db.pyloliod_state.find_one({'run_id': run_id})
        if taks_state is None:
            mongo.db.pyloliod_state.insert({'run_id': run_id, 'state': 1})
            from webservice.celery_task import create_plot
            print('try to start celery task')
            create_plot.delay(run_id)
        return jsonify({'status': -1, 'run_id': run_id, 'data': None})
    data = {item: {'div': plot_in_db[item + '_div'], 'script': plot_in_db[item + '_script']} for item in plots_list}
    print(data.keys())
    j = jsonify({'status': 1, 'run_id': run_id, 'data': data})
    return j


if __name__ == '__main__':
    the_app.run()
