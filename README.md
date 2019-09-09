# LEM Simulations

An environment to run Local Energy Market simulations


## Download data

1. Go to the source directory
2. Run ```sh
python download_data.py
```

## Run simulations
From the main directory:
```sh
parallel --verbose --header : --colsep ' ' python simulations/first_real_sim.py {Strategy} {Year} {Month} {Day} {Seed} {Algo} {Horizon} :::: simulations/parameter_set2.txt

```

## Generate plots
Also from the same directory
```sh
python simulations/plot_results.py
```


