# local call --> gunicorn -c gunicornconf.py  --reload wsgi:app

#import multiprocessing

# to be removed for Nginx on AWS 
#bind = '127.0.0.1:3000'


workers = 5
#workers = 2
#workers = multiprocessing.cpu_count()*2+1

loglevel = 'info'
#errorlog = os.path.join(_VAR, 'log/api-error.log')
#accesslog = os.path.join(_VAR, 'log/api-access.log')
errorlog = "-"
accesslog = "-"

timeout = 3 * 60  # 3 minutes
keepalive = 5 * 24 * 60 * 60  # 5 days
capture_output = True


# Environment variables
raw_env = ["MYCHAIN=talaonet", "MYENV=aws", "WEB3_INFURA_PROJECT_ID=f2be8a3bf04d4a528eb416566f7b5ad6"]