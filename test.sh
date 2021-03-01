mkdir -p test/resources/themes
cp -r deutschkurs test/resources/themes
reset && kb4it -force -theme deutschkurs -log DEBUG test html/