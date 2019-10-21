for y in instances/*.stp;
do
  echo "Teste: Instancia 10A2S5P10 em: " > log_"$y"
  date >> log_"$y"
  python3 main.py $y >>  GR_"$y"
  date >>  GR_"$y"
 done;