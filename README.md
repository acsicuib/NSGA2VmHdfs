This program has been implemented for the research presented in the article "Multi-objective Optimization for Virtual Machine Allocation
and Replica Placement in Virtualized Hadoop Architecture", accepted for publication in "IEEE Transactions on Parallel and 
Distributed Systems" journal.


This a NSGA-II algorithm implementation in python 2.7, considering the GA settings explained in the article. For more details, please, read the article in https://doi.org/10.1109/TPDS.2018.2837743

This program is released under the GPLv3 License.

**Please consider to cite this work as**:

```bash

@article{guerrero_multi-objective_2018,
	title = {Multi-{Objective} {Optimization} for {Virtual} {Machine} {Allocation} and {Replica} {Placement} in {Virtualized} {Hadoop}},
	volume = {29},
	copyright = {All rights reserved},
	issn = {1558-2183},
	doi = {10.1109/TPDS.2018.2837743},
	abstract = {Resource management is a key factor in the performance and efficient utilization of cloud systems, and many research works have proposed efficient policies to optimize such systems. However, these policies have traditionally managed the resources individually, neglecting the complexity of cloud systems and the interrelation between their elements. To illustrate this situation, we present an approach focused on virtualized Hadoop for a simultaneous and coordinated management of virtual machines and file replicas. Specifically, we propose determining the virtual machine allocation, virtual machine template selection, and file replica placement with the objective of minimizing the power consumption, physical resource waste, and file unavailability. We implemented our solution using the non-dominated sorting genetic algorithm-II, which is a multi-objective optimization algorithm. Our approach obtained important benefits in terms of file unavailability and resource waste, with overall improvements of approximately 400 and 170 percent compared to three other optimization strategies. The benefits for the power consumption were smaller, with an improvement of approximately 1.9 percent.},
	number = {11},
	journal = {IEEE Transactions on Parallel and Distributed Systems},
	author = {Guerrero, Carlos and Lera, Isaac and Bermejo, Belen and Juiz, Carlos},
	month = nov,
	year = {2018},
	note = {Conference Name: IEEE Transactions on Parallel and Distributed Systems},
	keywords = {Optimization, Cloud computing, Resource management, evolutionary computing and genetic algorithms, file replica placement, Genetic algorithms, hadoop, Power demand, Sorting, Virtual machine allocation, Virtual machining},
	pages = {2568--2581}
}

}
```

**Execution of the program**:

```bash
    python mainGA.py
```

**Acknowledgment**:

This research was supported by the Spanish Government (Agencia Estatal de Investigación) and the European Commission (Fondo Europeo de Desarrollo Regional) through Grant Number TIN2017-88547-P (AEI/FEDER, UE).
