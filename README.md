## United Perception

<img src=./up-logo.png width=50% />


## 文档

[up 官方文档](https://eod.readthedocs.io/en/latest/index.html)


###
```
#先编译本地代码
python setup.py build_ext -i

#执行ssd网络训练
python -u -m up train --ng=2 --nm=1 --launch=pytorch --config=configs/det/ssd/ssd-r18-300.yaml --display=100
#inference测试一张图片
python -u -m up inference --ng=1 --nm=1 --launch=pytorch --img_path=./test.png --ckpt=/root/ret18_ssd/save_dir/ckpt_e140.pth --config=configs/det/ssd/ssd-r18-300.yaml
执行结果保存在当前目录的vis_dir文件夹下面

#执行ssd网络量化
python -u -m up train --ng=2 --nm=1 --launch=pytorch --config=configs/quant/det/ssd/ssd-r18-w4a4-qdrop.yaml --display=100

#导出量化模型
python -u -m up quant_deploy --config=configs/quant/det/ssd/ssd-r18-w4a4-qdrop-deploy.yaml 


```
