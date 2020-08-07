###################################################################
# Command to run container after building:                        #
# $ sudo docker run -p 5000:5000 --env FLASK_APP="src" flasktest  #
###################################################################
FROM python:alpine3.8
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt 
EXPOSE 5000
CMD [ "flask", "run", "--host=0.0.0.0" ] 
