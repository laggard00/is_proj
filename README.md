# is_proj

# Bike rental app

## Opis projekta
Aplikacija omoguce pregled, dodavanja i rezervaciju bicikla, korisnici mogu narpaviti rezervacija za neki termin, a sustav automatski provjerava dostupnost. App je napravljen kao rjesenje za tvrtke koje se bave najmom bickla

## Funkcionalnosti
- Pregled svih bicikala
- Dodavanje, uređivanje i brisanje bicikla
- Pregled svih rezervacija
- Dodavanje nove rezervacije uz provjeru zauzetosti
- Označavanje rezervacija kao završene
- Pregled trenutno rezerviranih bicikala

## Pokretanje lokalno
1. git clone https://github.com/laggard00/is_proj.git ili git clone git@github.com:laggard00/is_proj.git
2. Otvoriti folder bike_rental
3. CMD/Powershell ili bash unutar tog foldera, i pozvati komandu `docker compose up --build` (Docker compose mora biti instaliran na računalu)
4. Frontend se vrti na localhost:8080 , backend na localhost:5000 a Postgres na localhost:5432
