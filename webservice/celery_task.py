from bokeh.embed import components
from celery import Celery
from six import iteritems

from strategy_ploting.strategy import Strategy
from .app import the_app, mongo


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(the_app)


@celery.task()
def create_plot(run_id):
    print('celery_task started')
    s = Strategy(run_id)
    plot_dict = {'plot_1': s.rolling_returns_plot,
                 'plot_2': s.rolling_returns_volatility_matched,
                 'plot_3': s.rolling_returns_log,
                 'plot_4': s.returns_plot,
                 'plot_8': s.top_drawdown_plot,
                 'plot_9': s.monthly_returns_plot,
                 'plot_10': s.annual_returns_plot,
                 'plot_11': s.dist_monthly_returns_plot,
                 'plot_17': s.position_exposure_plot,
                 'plot_18': s.top_positions_plot,
                 'plot_20': s.holding_plot,
                 'plot_21': s.turnover_plot,
                 'plot_25': s.round_trip_holding_time_plot,
                 'plot_26': s.round_trip_pnl_plot,
                 'plot_27': s.round_trip_return_plot,
                 'plot_28': s.scenario_plots[0],
                 'plot_29': s.scenario_plots[1],
                 'plot_30': s.scenario_plots[2],
                 'plot_31': s.scenario_plots[3],
                 'plot_32': s.scenario_plots[4]}
    dict_to_insert = {'run_id': run_id}
    for plot_name, plot in iteritems(plot_dict):
        if plot is not None:
            dict_to_insert[plot_name + '_script'], dict_to_insert[plot_name + '_div'] = components(plot)
        else:
            dict_to_insert[plot_name + '_script'], dict_to_insert[plot_name + '_div'] = None, None

    mongo.db.pyloliod_state.remove({'run_id': run_id})
    mongo.db.pyloliod.insert(dict_to_insert)

