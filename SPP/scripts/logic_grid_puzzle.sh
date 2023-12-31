MODEL="gpt4-32k" # your engine name

DATA_FILE="logic_grid_puzzle_200.jsonl"

START_IDX=31
END_IDX=60

METHOD="role" # ['standard','cot','spp', 'spp_profile', 'spp_fixed_persona']

# w/ or w/o system message (spp works better w/o system message)
SYSTEM_MESSAGE="" # or e.g., "You are an AI assistant that helps people find information."

python run.py \
    --model ${MODEL} \
    --method ${METHOD} \
    --task logic_grid_puzzle \
    --task_data_file ${DATA_FILE} \
    --task_start_index ${START_IDX} \
    --task_end_index ${END_IDX} \
    --system_message "${SYSTEM_MESSAGE}" \
    ${@}

