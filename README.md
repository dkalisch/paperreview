# Paper Review System
## About
To be able to treat the visitors of the conference and the authors of the submitted papers as customers, it is necessary to have all the data about them together in one place, to be able to unite the data of a paper author, who is also participating in the conference as visitor or speaker. Most academic conferences suffer from having multiple systems for different purposes, such as event registration, paper submission or paper review. These system do not share their data and do not have a mutual database. Therefore, it is not possible to combine data from a participant, who is also a paper author, since his data is distributed over several data pools. If the data from both systems is matched and combined, it can be analyzed to examine user needs and to improve the quality of the conference.

## Odoo
> Odoo (formerly known as OpenERP[1] and before that, TinyERP) is a suite of open-source enterprise management applications. Targeting companies of all sizes, the application suite includes billing, accounting, manufacturing, purchasing, warehouse management, and project management.([see  Wikipedia](https://en.wikipedia.org/wiki/Odoo))

## Paper review module
The module in this repository adds a paper submission system to the odoo v9 ERP framework.

## Recuiremnets
Before you can install the paper submission system, please ensure, that you have installed `pythin-magic`.

    pip install python-magic

You also might want to install the `partner_naming` module from [https://github.com/tobwetzel/partner_naming](https://github.com/tobwetzel/partner_naming).

## Installation
To install the module simply copy the source code from this repository to your folder for own modules and update the odoo system by reloading it. After this, log in into the administration account of odoo, go to the modules section, locate the paper review module and click the `Install` button.

## License
This software is a paper review system module for the ERP system [odoo](http://www.odoo.com).
The software was developed by Tobias Wetzel and Dominik Kalisch and published under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license](http://creativecommons.org/licenses/by-nc-sa/4.0/deed.en). By downloading the software you agree to this license.

A more elaborated description will follow.