# Project purpose

Every single day, millions of people transit the main cities of the world, in a restless dynamic flow that makes these capitals alive, giving them their identity and soul. Since the raise of big data at scale, billions of those movements have been registered in many different ways and forms, providing a unique opportunity to exploit them to better understand how those movements work.

This project aims to create a scalable probabilistic model for geographical demand. The proposed model applies to any use case where a signal can be measured given both it's position (latitude and longitude coordinates) as well as the precise moment it happened (time). Some examples of this behaviour are:

- On-demand pick up services, such as Uber, Cabify, etc...
- Pedestrian-traffic intensity tracking

The complete project explanation below focuses on just one data set (Uber pickups) to illustrate the overall approach, but could be applied to many other use cases. In summary, this document will cover the following aspects:

- Data analysis and preprocess: all the transformations applied prior to modelling
- Modelling: step-by-step assumptions and approach considered
- Results: overview of the model output and further improvement actions
<!-- ABOUT THE PROJECT -->


<!-- GETTING STARTED -->
## Getting Started

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/ignacio-marin/Geo-Demand
   ```
2. Pip install packages
   ```sh
   pip install -r requirements.txt
   ```
