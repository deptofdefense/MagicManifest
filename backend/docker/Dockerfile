FROM python:3.11
RUN mkdir /application
COPY requirements.txt /application/requirements.txt
COPY . /application
WORKDIR /application
RUN pip install --no-cache-dir --upgrade -r /application/requirements.txt
# If running makeApp.py, change to EXPOSE 5000 and to CMD ["python", "makeApp.py"]
# EXPOSE 8000 
# CMD ["python", "makeApi.py"]

EXPOSE 5000
CMD ["python", "makeApp.py"]