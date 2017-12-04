#!/bin/bash

cat $1 | awk '{print $2}' | sort -u > train_relations.lst
cat $2 | awk '{print $2}' | sort -u > validation_relations.lst
cat $3 | awk '{print $2}' | sort -u > test_relations.lst


cat $1 | awk '{print $1"\n"$3}' | sort -u > train_entities.lst
cat $2 | awk '{print $1"\n"$3}' | sort -u > validation_entities.lst
cat $3 | awk '{print $1"\n"$3}' | sort -u > test_entities.lst

echo "TRIPLES"
echo "in training set"
wc -l $1
echo "in validation set"
wc -l $2
echo "in test set"
wc -l $3

echo "RELATIONS"
echo "unique in training set"
cat train_relations.lst | wc -l
echo "unique in validation set"
cat validation_relations.lst | wc -l
echo "unique in test set"
cat test_relations.lst | wc -l

echo "in validation set but not training set"
comm -23 validation_relations.lst train_relations.lst | wc -l
echo "in test set but not training set"
comm -23 test_relations.lst train_relations.lst | wc -l

echo "ENTITIES"
echo "unique in training set"
cat train_entities.lst | wc -l
echo "unique in validation set"
cat validation_entities.lst | wc -l
echo "unique in testing set"
cat test_entities.lst | wc -l

echo "in validation set but not training set"
comm -23 validation_entities.lst train_entities.lst | wc -l
echo "in test set but not training set"
comm -23 test_entities.lst train_entities.lst | wc -l

rm *lst
