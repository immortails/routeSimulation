### 描述
#### 基础架构
- 以1ms为仿真步长进行仿真
- 仿真采用排队论与图论的方式对节点和边建模
#### 强化学习部分
- 框架已使用经验队列，后序还要加入target network来提高
- 已实现基础价值学习部分，后序准备用duling network来改进价值学习；以及用actor critic方法来学习
#### todo
- 神经网络update部分(已完成)
- reward部分(已完成)
- target network
- duling network
- actor critic
#### 更新日志
**2月17日**：
- 在网络特征中加入节点状态特征，更新了GNN模型以及整个DQN路由算法
- 节点改成每个链路一个缓冲区的形式，更符合原理