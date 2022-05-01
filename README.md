1. Hello World 

- The initial step of this project was to select a website to base this webscraper on. I have had a longstanding interest with cryptocurrency so I decided to use this as my base 

- One of (if not the largest) tracking websites of cryptocurrencies, is coinmarketcap.com. For this project, then, I will be scraping data off their website by building a framework which can scalably store this data & run a virtual version of my scraper :) 


2. Prototyping the webscraper 

- Before being able to access the website, a cookies iframe had appeared. In the initializer the webscraper was designed to immediately click this so that the webpage could then begin to be manipulated. 

- The second hurdle in this project was creating a class which could navigate the website & swap in-between web pages. Two key methods had been tested: scrolling until the next element became visible, and scrolling by a certain pixel amount. At this point both were viable options. 

- In order to swap pages the webscraper also had to be able to have the next page button visible before attempting to click it. 


3. Retrieving details 

- Now that the website could be successfully navigated I could begin the process of scraping data. After some trial & error I found that the best way to structure this would be within a dictionary comprehension. 

- For each element in this list of dictionaries we would need to have identifiable bits of information. For this, a UUID string was utilized to act as a global unique identifier 

- For a more obvious identifier we also collected each coins’ name & symbol, which being cryptocurrency coins will always be unique. Other pieces of key information about coins were also collected, such as their market cap & price. 

- Some coins would have missing attributes, such as a missing price. For these a NoSuchElementException was used in order to skip these results without crashing the webscraper. 

- These details were saved as a json file by creating a write method which used the json.dump() method. Here, it is important to note a funny setback I encountered. Whilst attempting to test this json file json.dumps was used unnoticed so all that my testing methods were attempting to analyse a string object rather than the list of dictionaries in json format as intended. 

- Alongside this, an additional mothod was used to save the image data for each coin. This was inserted inside the same loop which collected coin attributes; in this instance the image url was collected & appended to the coins dictionary. 


4. Documentation & testing 

- As the code project had now reached a point where it was in a draft version with features working as intended, docstrings were added to explain the use of each method to make it far easier to understand the logic & reproduce this webscraper in the future. 

- Now we had an output in the form of a json file with all of our results, an additional testing file could be created to ensure that for future runs any errors could be more easily traced back using the inbuilt unittest module. 

- For the testing of this project we would only initialize a few tests as more would be created as the project progressed; at the moment these tests checked that all dictionary keys existed, that the json file was a list & that inside of that list dictionaries existed 


5. Scalably Storing Data 

- Images are stored with the cryptocurrencies’ Symbol as an identifier. Originally a method was created that would save the images as a .png file LOCALLY which could be uploaded, however this would create problems in importing to SQL & taking a large amount of time to upload correctly to AWS S3. Instead, image data is saved via the images & then appended to our main coins_data.json file. 

- A method was created which could then later separate this data into a list of the image urls; from here, we used the urlib import to save the images .jpg associated with the image url. Instead of saving the images locally, a temporary dictionary was used to transform the image url's to .jpeg & immediately send the images to the AWS S3 bucket without saving them locally 

- All coin information data was uploaded to an AWS S3 bucket stored as a json file. This data was then connected to an AWS RDS instance via a Boto3 method combined with turning the json file into a pandas dataframe – from here we can connect to a postgreSQL server to manipulate the data in an SQL format. 


6. Getting more data 

For this section of the project the main aim was to collect a substantial amount of results & ensure no duplicates: 

- To collect more data, a method was created which would click the next page button at the bottom of the page until the webscraper had reached page 11; then, the same method responsible for swapping pages would terminate the webpage. 

- Each coin from coinmarketcap had a unique ID with the coin name attached to the end. By extracting this as a string and splitting the string so just the coin name was used as a friendly ID, I could store this & adapt my scraping method so that if this name appeared the scraper would not scrape this already 
known data 

- As the image data was also attached in this loop when the Friendly ID was found it would also prevent the image data from being scraped too 


7. Making the scraping scalable 

- Beforehand the only way to ensure no duplicate results was through a friendly-ID,  a connection the our RDS is established & using sqlalchemy and psycopg2 scraped data can be compared against data on the RDS & a SQL command is used to only allow DISTINCT results to be recorded (unique results)

- Now in order to make the data scalable we would have to install our project on a docker image that could be run & an amazon EC2 instance that could also be run. 

In order to begin this first preparations would be needed for the project: 

- Chromedriver was moved to the same directory as our project 

- A Dockerfile was created to give docker instructions to read & download requirements, the instructions to download & unzip a google chrome package, to update any packages, & then to run the correct files 

- All results which were stored in local directories had to have filepaths changed from e.g. 'patrick/project/coin_data.json' to './coin_data.json' this in turn would enable docker to find a existing filepath (docker cannot view local filepaths as it is a disconnected system) 

-In the initialiser of the webscraper an additional headless argument is used to allow our project to run without any GUI (scary) 
Creating the Docker image: 

- Dockerhub account was created & docker was downloaded via the CLI; using sudo commands we are able to login to docker & view all current images, though as of right now there are none 

- Whilst inside the cd which contains the project, dockerfile & requirements we can now use the docker build command to build our image. Here it is good to note that docker will only build the files that are explicitly mentioned within the Dockerfile within the project & will only install packages contained within the requirements.txt file. 

- Another key feature to note is that when building the image the -t (tag) argument is used to name the docker image. This is important; later on, when we attempt to pull the Docker image, we will only be able to pull images that begin with our username i.e. myname/scraperproject. 

- Now that the image has been built we can log into to our docker account in the CLI and, using 'sudo docker run -it myname/scraperproject', can run the webscraper within docker. Arguments are placed within the initializer of the scraper to allow for running of the scraper in headless mode. 

Running the scraper via EC2: 

- As with running our scraper via docker, this involves not running the project locally. In this context we are now running the scraper using an AWS EC2 instance (using AWS virtual servers). 

- In order to do this we first setup a free tier EC2 instance and gain our keypair which must be chmod 400 encrypted. We can then, using the CLI, paste our instance via its public DNS, which will detect our encrypted keypair & allow access to the instance. From here we can just sudo login to our docker account and, like before, pull our docker image to be run on the ec2 instance 


8. Monitoring and Alerting 

Setup Prometheus: In order to monitor the webscraper via the EC2 instance a container must be created to connect to Prometheus. For Prometheus to function correctly on MacOSX three different adjustments must be created: 

- Using the dockerhub desktop application within the settings/engine, we must add an additional argument which will allow for a metrics IP address to be connected to the image 

- A prometheus.yml file must be created in the root directory to allow the docker image to connect to Prometheus for monitoring 

- A Prometheus Daemon file is also created which will also allow access to the Prometheus monitoring software 
Once created we can run the Prometheus container within the docker image using the VERY longwinded command 'sudo docker run --rm -d
--network=host
--name Prometheus
-v root/prometheus.yml:/etc/prometheus/prometheus.yml
prom/prometheus
--config.file=/etc/prometheus/prometheus.yml
--web.enable-lifecycle' 
This will allow for Prometheus connections; to finish this, we restart the docker image and, pasting the IP used to connect Prometheus into the search bar, can check to see if our EC2 is connected 
This Prometheus connection is now connected to Grafana (an open source analytics engine). From here a dashboard is created; for my project I had chosen to create graphs to monitor: 

- Query duration 
- Website http response size 
- Container action size 
- Engine health 


9. CI/CD 

As learnt previously it takes quite a while to update docker images with code changes, time to streamline this using CI/CD! 

- Firstly, Github secrets are made. These credentials will mean that whenever we push new changes to github (and so the docker image) we won't have to enter credentials each time. These secrets are inaccessible to anyone after creation & are stored on the projects repository 

- A Github action is created. Github provides templates for these actions; a basic one is used to automate updates to the docker image each time the repository is updated & push it to dockerhub for usage on the EC2 Instance 

- The very final objective of this project is to have the scraper run automatically. For my scraper I used cronjobs within my EC2 instance to have the webscraper run daily at 10am without user input; from this my grafana dashboard can be checked to ensure that the webscraper ran correctly 
