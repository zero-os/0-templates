## 0-Templates [![Build Status](https://travis-ci.org/zero-os/0-templates.svg?branch=master)](https://travis-ci.org/zero-os/0-templates) [![codecov](https://codecov.io/gh/zero-os/0-templates/branch/master/graph/badge.svg)](https://codecov.io/gh/zero-os/0-templates)


This repo contains zero-os templates that can be managed by [0-robot](https://github.com/Jumpscale/0-robot).


Upcomming releases:

- [0.1](https://github.com/zero-os/0-templates/milestone/1)
  - Move bootstrap and node templates from 0-robot to 0-templates.
  - Adapt [hardwarecheck and erp_registeration](https://docs.greenitglobe.com/ThreeFold/itenv_asset_management/src/branch/master/templates) templates to zero-robot and add them to 0-templates.
  - Create a 0-robot flist.
  - Extend node template to install 0-robot on the node.
  - Add automated tests.
  - Add README.md for each template.

- 0.x
  - Kubernetes template:
    - Deploys kubernetes master cluster with x workers.
    - Workers get raw storage volumes or work with qcow files.
  - Zero-stor daemon template:
    - Deploys 0-store daemon on a disk.
  - Zero-stor client template:
    - Self-heals a namespace.
  - Minio template:
    - Deploys minio S3 over x nodes with zero-stor backend.



Contribution:

Please check the [contribution](./docs/contribution.md) guidelines before contributing to this repo.
