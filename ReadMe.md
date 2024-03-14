# RAG Application on PDF files with Mistral API, ChromaDB and llama_index

## What is RAG Application ? 

To enable large language model to also have knowledge of data outside of its training data, e.g. company or research data, you can embed this data into a vector database and let an LLM retrieve the relevant documents and data. The LLM will then construct a coherent answer with the retrieved data. It enables you to connect pre-trained models to external, up-to-date information sources that can generate more accurate and more useful outputs.

## How does it works ?

The first steps in this process are as follows:
- Downloading PDFs.
- Cutting into chunks of a given size (max token).
- Embedding the chunks.
- Storing the embeddings in a vector database.
To do this, we use the `llama_index` library, which provides ready-to-use functions, and `chromaDB` vector database.

The following steps involve the use of LLM:
- Embedding of the question.
- Calculation of the closest similarities between the PDF embeddings and the question one.
- Finally, the question and the chunk are sent to the LLM to generate a response.
To do this, we're using the `streamlit` library, which provides a user interface based on python code, and the `Mistral API` to connect to the LLM.

## Requirements

The experiments were performed on a local laptop without GPU. In addition, Python version 3.10.11 and the dependencies in [requirements.txt](./requirements.txt) were used. These can be installed in a virtual environment with the following commands:
```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install upgrade pip
pip install -r requirements.txt
pip install -e .
```

**Note**: our experiments were conducted with the exact package versions specified in `requirements.txt`. Future updates may alter reproducibility. 

## Unit testing

To run unit tests, the user can add tests to the `test_app.py` file and run the command:
pytest test_app.py
```sh
pytest test_app.py
```

## Running

To use this repository, the user must copy the PDFs into the `data` folder and use the following command to execute the code: 
```sh
streamlit run main.py
```
This will generate an interface for asking questions and reading answers from the LLM.

### *Note running on AWS ECS with AWS ECR
#### Setup for ECR
- First, build a docker image with the `Dockerfile`
```sh
docker build -t image_name .
```

- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

- Create an AWS ECR repository to store the docker image.

- Create an IAM User

- Create an access key

- Cdd permission to the user

- Cdd the accees key via the aws configure CLI (in vscode)

- Create an IAM user group and add the following permission to be allowed to push AmazonEC2ContainerRegistryFullAccess

- Log to your ECR reposytory with VScode terminal 
```sh
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin your_ECR_repo_URL
```

- Tag the docker image with the ECR repo 
```sh
docker tag your_docker_image your_ECR_repo_URL
```

- Push it 
```sh
docker push your_ECR_repo_URL
```

#### Setup for ECS

- Create a cluster

- Create a new task definitiion family

- Create an EC2 instance (ask for new limit quota if needed AWS Support)

- Create the task in the ECS cluster with the EC2 instance and the task definition family and link it to the ECR repository.

- For each modifcation to the local code, rebuild the Docker image, push it to ECR and deploy it on ECS. This can be done with CI/CD, i.e. by pushing to GitHub, which will test the code on the GitHub action, create the Docker image and automatically deploy it to AWS.

At the end of the development process, store the mistral model on AWS EC2 and link it to the application on ECS to avoid downloading it each time the application is launched. Same for the chromaDB database ?

To resume: For ECS with EC2, you assign resources to tasks to manage how the instance's resources are used. You pay for the EC2 instance, not directly for each task.

### *Note running on Sagemaker

- Open an instance `ml.g4dn.xlarge`

- Open a terminal
```sh 
cd SageMaker
git clone -b Local_LLM_with_AWS "https://github.com/Argencle/RAG_PDF_QA.git"
cd RAG_PDF_QA
conda create -n myenv nodejs=20.9.0 -c conda-forge -y
source /home/ec2-user/anaconda3/bin/activate myenv
npm install -g localtunnel
pip install -r requirements.txt
streamlit run main.py
```

- Open another terminal 
```sh
source anaconda3/bin/activate myenv
curl https://ipv4.icanhazip.com (used to obtain your public IP address)
lt --port 8501 (enter your IP address as tunnel password) (creates a secure tunnel from the public web to an application (here streamlit) running  on a local machine on a specific port (8501))
```

*Note that the link of the streamlit application can be shared to anyone !

## To add
To deal with bigger files:
- Choose a model specialized in this kind of task (with a bigger context window than Mistral 32k tokens)
- Do hierarchical summarization