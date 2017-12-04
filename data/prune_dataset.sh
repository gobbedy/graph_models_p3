#!/bin/bash

# remove invalid entities from the datasets
# this is done iteratively, because when we remove triples that contain an invalid entity from the training dataset, we may have removed
#   the only instance of an otherwise valid entity, but without removing the same entity in the test/validation set
# once invalid entities are removed from all datasets, the validation and test sets may have relations that are not found in training set
# therefore we then remove the latter relations from the validation and test sets

# list of invalid entities (ie entities for which a word2vec vector was not found)
grep ', 0, 0, 0, 0' entitiesTrain_vec.csv | grep -v entity | awk '{print $1}' | grep -oP '[^,]+' > invalid_entities

training_set=freebase_mtr100_mte100-train.txt
validation_set=freebase_mtr100_mte100-valid.txt
test_set=freebase_mtr100_mte100-test.txt

echo "BEFORE PRUNING"
pruning_info.sh $training_set $validation_set $test_set

# REMOVE INVALID ENTITIES from datasets
entity_prune_done=0
while [ $entity_prune_done -eq 0 ]; do

    # remove triples containing invalid entities from each set
    ## '-v' means print lines not containing this pattern
    ## '-w' means match lines containing this pattern as a whole word (so together with -v, print lines not containing this pattern as a whole word)
    ## '-F' means interpret the patterns as string literals, not a regex
    ## '-f' means take the patterns from a file (here invalid_entities) rather than the command line; each pattern assumed to be on a separate line
    grep -vwFf invalid_entities $training_set > train_pruned.txt
    grep -vwFf invalid_entities $validation_set > validation_pruned_entities.txt
    grep -vwFf invalid_entities $test_set > test_pruned_entities.txt

    # removing these entities will cause some entites to vanish from training set but not validation/test set. so we list all such entities
    cat train_pruned.txt | awk '{print $1"\n"$3}' | sort -u > train_pruned_entities_unique
    cat validation_pruned_entities.txt | awk '{print $1"\n"$3}' | sort -u > validation_pruned_entities_unique
    comm -23 validation_pruned_entities_unique train_pruned_entities_unique > unique_validation_entities
    cat test_pruned_entities.txt | awk '{print $1"\n"$3}' | sort -u > test_pruned_entities_unique
    comm -23 test_pruned_entities_unique train_pruned_entities_unique > unique_test_entities

    # add these entities to the list of invalid entities. if there are none, stop iterating
    cat unique_validation_entities unique_test_entities | sort -u > new_invalid_entities
    if [[ ! -s new_invalid_entities ]]; then
      # empty file, so no new valid entities found, thus we can stop iterating
      entity_prune_done=1
    fi
    cat new_invalid_entities >> invalid_entities
    rm new_invalid_entities

done

# keep only vectors kept in pruned training dataset from word2vec set
grep -wFf train_pruned_entities_unique entitiesTrain_vec.csv > pruned_vec.csv

# REMOVE INVALID RELATIONS
# remove from pruned test set any relation that appears in pruned test data but not in pruned train data (only 4 such relations)
cat train_pruned.txt | awk '{print $2}' | sort -u > unique_train_relations.txt
cat test_pruned_entities.txt | awk '{print $2}' | sort -u > unique_test_relations.txt
comm -23 unique_test_relations.txt unique_train_relations.txt > invalid_test_relations
grep -vwFf invalid_test_relations test_pruned_entities.txt > test_pruned.txt

# remove from pruned validation set any relation that appears in pruned validation data but not in pruned train data (only 1 such relation)
cat validation_pruned_entities.txt | awk '{print $2}' | sort -u > unique_validation_relations.txt
comm -23 unique_validation_relations.txt unique_train_relations.txt > invalid_validation_relations
grep -vwFf invalid_validation_relations validation_pruned_entities.txt > validation_pruned.txt

# keep list of relationships in training set for training autoencoder
mv unique_train_relations.txt pruned_relations.txt

rm invalid* unique* *pruned_entities*

echo "AFTER PRUNING"
pruning_info.sh train_pruned.txt validation_pruned.txt test_pruned.txt
