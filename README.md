# Anonymous Project

This repository provides an official implementation of a paper that under double-blind review. The repository will be de-anonymized and released to the public after the review process.


## Getting started

To adversarially train a ResNet-18 model against $L_2$-norm attack by the free-AT algorithm, run: 
```
python train.py   --data cifar10  --method free  --attack L2  --eps 128.0  --model res18  --save_path cifar10_l2_free
```

To evaluate the model against [AutoAttack](https://github.com/fra31/auto-attack), run: 
```
python test_autoattack.py  --model_path cifar10_l2_free  --data cifar10  --attack L2  --eps 128.0  --seed 1 
```

