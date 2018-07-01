FROM python:3-onbuild
RUN apt-get update && apt-get install -y software-properties-common curl
COPY requirements.txt /
RUN pip install -r requirements.txt
RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"; echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get -y install google-cloud-sdk
COPY Lambo-89cff3bde0ba.json /notkeys/googlenotkey.json
ENV GOOGLE_APPLICATION_CREDENTIALS /notkeys/googlenotkey.json
RUN gcloud auth activate-service-account --key-file=/notkeys/googlenotkey.json
CMD ["python","-u","./main.py"]