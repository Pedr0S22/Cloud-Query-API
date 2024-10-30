# Sistema de Gestão de Dados  - Trabalho Prático

Depending on the computer architecture that you have in your computer, you may face some issues installing psycopg2.
This happens especially if you have Apple M1 Pro or Apple M2 Pro.

To fix it, install the following libraries:

```
brew install openssl
brew --prefix openssl
brew install libpq
```

With the result of `brew --prefix openssl`, you will see the location that openssl was installed. 
In my case, I got `/opt/homebrew/opt/openssl@3`. 
If you have something different, replace the path in the following commands:

```
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib -L/opt/homebrew/opt/libpq/lib"
export CPPFLAGS="-L/opt/homebrew/opt/openssl@3/include -L/opt/homebrew/opt/libpq/include"
```

After that, install the `psycopg2-library`. You may have a different python version. In that case, replace properly:

```python3.13 -m pip install psycopg2-binary```

This link may be useful: https://stackoverflow.com/questions/66888087/cannot-install-psycopg2-with-pip3-on-m1-mac


## Authors

* SGD 2024 Team
* University of Coimbra

