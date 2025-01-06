Write a program in asynchronous Python to crawl a site by links.
The input is the site address
for example
https://ru.wikipedia.org/
then the parser follows all the links found on the page.
opens the page and searches for links again.
While following the links
Words are counted.
The output is the top 10 most popular
Provide the ability to control the number of simultaneous requests to the site.
Provide for setting the crawl depth.
the program must have type annotations and pass the mypy check.

To run the project, you need to install dependencies using the command
pip install -r requirements.txt
To run the word count, use the command
make run
To run mypy, use the command 
make typecheck