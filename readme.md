### 描述
#### 基础架构
- 以1ms为仿真步长进行仿真
- 仿真采用排队论与图论的方式对节点和边建模
- 节点建模成多个队列，边一个队列
#### 强化学习部分
- 框架已使用经验队列
- 已实现基础价值学习部分，后序准备用duling network与target来改进价值学习；以及用a2c与ppo的方法来学习
#### todo
- 神经网络update部分(已完成)
- reward部分(已完成)
- target network(已完成)
- duling network(已完成)
- a2c
- ppo
#### 更新日志
**2月17日**：
- 在网络特征中加入节点状态特征，更新了GNN模型以及整个DQN路由算法
- 节点改成每个链路一个缓冲区的形式，更符合原理
- 修正了当链路打满时，程序会卡死的bug
- 调整了链路模型，用队列来替换优先队列，提高性能。
**2月18日**：
- 修正学习率参数，模型成功收敛
- 修正reward，用历史的评估分数来比较，而不是上次的，收敛速度变快。
**2月19日**:
- 发现了status导致内存泄露的问题，暂时去掉该功能，对链路利用率和节点利用率的记录上也有相应的内存泄露问题，暂时去掉。
**2月20日:
- 记录了时延，时延抖动，丢包率等指标，优化了参数保存记录与画图功能。
- 写完了dueling与target合并的D3QN。