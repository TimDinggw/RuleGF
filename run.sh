#!/bin/bash

n_all=1 # run continuously n_all times
n=5 # iteration number
data_dir="data/CrossLPData/DBP-FB" # dataset

source ~/anaconda3/etc/profile.d/conda.sh
conda activate pyclause

scripts="link_prediction/data_process.py link_prediction/learn.py link_prediction/eval.py link_prediction/learn_to_predict.py link_prediction/predict_tails.py entity_align/run.py link_prediction/learn-cross.py link_prediction/eval-cross.py expand.py"

for ((run=1; run<=n_all; run++)); do
    log="log$((run+0)).txt"
    echo "" > "$log"
    
    overall_start_time=$(date +%s)
    echo "=== Starting run $run at: $(date) ===" >> "$log"

    for d in $data_dir/*; do
        folder_name=$(basename "$d")
        is_pure_number=1
        if [[ ! "$folder_name" =~ ^[0-9]+$ ]]; then
            is_pure_number=0
        fi
        if [ $is_pure_number -eq 1 ]; then
            echo "Deleting pure number folder: $d" >> "$log"
            rm -rf "$d"
        fi
    done

    script_loop_start_time=$(date +%s)
    echo "--- Script loop started at: $(date) ---" >> "$log"
    
    for ((i=1; i<=n; i++)); do
        echo ">>> Starting iteration $i at: $(date)" >> "$log"
        iteration_start_time=$(date +%s)
        
        for s in $scripts; do
            echo "Running $s, iteration $i" >> "$log"
            script_start_time=$(date +%s)
            python -u $s --data_dir $data_dir >> "$log" 2>&1
            script_end_time=$(date +%s)
            script_duration=$((script_end_time - script_start_time))
            echo "Script $s execution time: $script_duration seconds" >> "$log"
        done
        
        iteration_end_time=$(date +%s)
        iteration_duration=$((iteration_end_time - iteration_start_time))
        echo "<<< Iteration $i completed, duration: $iteration_duration seconds" >> "$log"
    done
    
    script_loop_end_time=$(date +%s)
    script_loop_duration=$((script_loop_end_time - script_loop_start_time))
    echo "--- Script loop ended, total duration: $script_loop_duration seconds ---" >> "$log"
    
    overall_end_time=$(date +%s)
    overall_duration=$((overall_end_time - overall_start_time))
    echo "=== Run $run completed, total duration: $overall_duration seconds ===" >> "$log"
    
    hours=$((overall_duration / 3600))
    minutes=$(( (overall_duration % 3600) / 60 ))
    seconds=$((overall_duration % 60))
    echo "=== Total execution time for run $run: ${hours}h ${minutes}m ${seconds}s ===" >> "$log"
done