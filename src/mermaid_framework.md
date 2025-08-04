```mermaid
graph TD
    ENV[环境输入]

    subgraph PCT[预测处理]
        PE[预测误差]
        IM[内部模型]
        PS[预测信号]

        subgraph WSI["嵌套工作空间实例 (WSI)<br/>(马尔可夫毯)"]
            style WSI stroke-dasharray: 5 5
            NG["s_wsi (感觉状态)<br/>神经门控"]
            IR[信息路由]
            MR["记忆重建<br/>(海马体)"]
            AXI[IPWT公理]
            INT["μ_wsi (结构)<br/>Ω_t / DMN 网关"]
            QUA["μ_wsi (现象)<br/>Qualia"]
            BCST["a_wsi (主动状态)<br/>WSI 广播 / ECN"]
        end
    end

    ENV --> PE
    PE -->|无意识处理| IM
    IM --> PS
    PS --> ENV
    PE -->|ε| PI(("PI"))
    IM --> PI

    PE -->|显著误差| NG
    NG --> IR
    IR --> AXI
    AXI -->|定义度量| INT
    INT -->|生成| QUA
    QUA -->|功能性标记| BCST

    IR --> MR
    MR -->|预测性检索| IR
    BCST -->|"主动推断<br/>(元推断)"| IM
    MR <-->|误差驱动更新| IM

    IIT[IIT现象学公理]:::iit
    QUA -. 描述 .-> IIT

    INT -.->|近似| PHIR(("Φ_R"))
```
