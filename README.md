## django 서버 실행방법
 kido-serviceKey.json 디스코드에 있습니다.
 
### windows 설정
1. 먼저 kido-serviceKey.json을 root폴더 밑에 놔주세요.
2. root폴더에서 python -m venv venv 터미널 입력
3. cd venv
4. Scripts/activate.ps1 터미널 입력(안된다면 powershell을 관리자 권한으로 실행후 Set-ExecutionPolicy Unrestricted 입력 후 y입력)
5. pip install -r requirements.txt
6. cd .. root폴더로 나옴
7. manage.py가 있는 폴더에서 python manage.py makemigrations
8. manage.py가 있는 폴더에서 python manage.py migrate
9. manage.py가 있는 폴더에서 python manage.py runserver
    
### MAC 설정
1. 먼저 kido-serviceKey.json을 root폴더 밑에 놔주세요.
2. root폴더에서 python3 -m venv venv 터미널 입력
3. cd venv
4. ls 후 bin폴더가 있는것을 확인
5. source bin/activate
6. root 폴더에서 pip3 install -r requirements.txt
7. manage.py가 있는 폴더에서 python3 manage.py makemigrations
8. manage.py가 있는 폴더에서 python3 manage.py migrate
9. manage.py가 있는 폴더에서 python3 manage.py runserver





