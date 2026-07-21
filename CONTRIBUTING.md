Event:CREATE PROJECT
	git clone https://github.com/wellmanifest/new-project.git
	IF NOT EXISTS  CREATE FILE README.MD 
	IF NOT EXISTS CREATE HEADER DESCRIPTION in file READMME.md
	UPDATE HEADER DESCRIPTION in file README.md
	IF NOT EXISTS CREATE FILE LICENSES.md 
	IF not EXISTS CONTENT UPDATE CONTENT in FILE Linces.md 
	CREATE GIT TAG as VERSION
	IF NOT EXISTS CREATE FILE VERSION.md 
	UPDATE VERSION TAG from git in version file 
	IF NOT EXISTS CREATE FILE TODO.md
	CREATER HEADER as GIT VERSION in TODO.md
	UPDATE HEADER CHECKLIST IN FILE TODO.md
	UPDATE project base on TODO list
	IF NOT EXISTS CREATE FILE CHANGELOG.md 
	Jęsli wszystkie zadanie z TODO zostały wykonane to przeniesc ten caly header do CHANGELOG jako HEADER z wykonanymi zadaniami
	CONTINUE
	
EVENT:CREATE PROMPT 
	IF NOT EXISTS CREATE PROJECT
  IF NOT EXISTS CREATE PROJECT.SH
	CREATE PROMPT.CONTENT:
    Masz stworzyc plik md w folderze docs podsumuwajacy co aktualnie jest wykonane i co jest do wykonania
    Wyciagnaj z kontekstu zadanie i zapisz je w liscie zadan w TODO.md
    Załącz pliku z folderu PROJECT i zaktulizowaj liste zadan TODO.md 
    
Event:CREATE PROJECT.SH 
  git clone https://github.com/wellmanifest/new-project.git 
  COPY project.sh to PROJECT 
  RUN project.sh
  
	