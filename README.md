# pytemplete


## Download data

1. Go to the source directory
2. Run ```sh
python download_data.py
```
3. Enjoy


## Run simulations

```sh
parallel --verbose --header : --colsep ' ' python simulations/first_real_sim.py {Strategy} {Year} {Month} {Day} {Seed} {Algo} {Horizon} :::: simulations/parameter_set.txt
```

