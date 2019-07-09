# data-portal

----

The Sparc Data Portal is an open source web application that provides insight into the data that is generated by the NIH Common Fund's Stimulating Peripheral Activity to Relieve Conditions (SPARC) program.

----

## Install Flask Dependencies
`pip install -r requirements.txt`

## Run in Development Mode
Make sure you have the correct environment variables set (see wiki). Then, in separate terminal windows, run:

```
make clean
npm run dev-build-dashboard
npm run dev-build-browse
make serve
```

## To start developing for the SPARC Data Portal
Please check out the documentation in the [Wiki pages](https://github.com/nih-sparc/data-portal/wiki) associated with this repository. 

## To interact with the SPARC data 
Please visit [https://data.sparc.science](https://data.sparc.science)
