# Discord AI chatbot with Tensorflow and NLP

* install
```sh
pip3 install pipenv
pipenv shell
pipenv install
python -c "import nltk;nltk.download('punkt')"
```

## commands

* Register discord user and manually give status 1 for admin status.
```sh
-register @you
```

### Teach bot example
* Add responses.
```sh
-teach I am doing fine thank you!
```
![alt](https://i.imgur.com/KUK4TbS.png)

* Add patterns.
```sh
-pattern how you doing tag:1
```
![alt](https://i.imgur.com/bQA8RAA.png)

### Train bot
* Usage
```sh
-trainer <epochs> <batch_size> <option> # Train patterns
-trainer <epochs> <batch_size> <option> # Train reponses
```

* example:
```sh
-trainer 1024 128 0
-trainer 1024 128 1
```