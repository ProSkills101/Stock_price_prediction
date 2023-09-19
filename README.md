# Stock_price_prediction

A beta model (referenced from multiple others) used for gathering stock infromation and displaying future forecasts. This can be run from (nearly) all python 3 environments. This is still in development, so feel free to report bugs and make your own contributions!

## Requirements

In addition to having an environment with python (I use python 3.9.12 for reference), the following packages are also required:
* numpy 1.21.5
* pandas 1.4.2
* pandas_datareader 0.10.0
* pandas ta 0.3.14b
* yfinance 0.1.70
* dash 2.5.0
* plotly 5.6.0
* quandl 3.7.0

Still, though, it is highly recommended that you update the packages to the latest version possible.

## Getting started

Once you have finished setting up the environment, simply go to your console and type the following:

``` py chart.py ```

The console should return the below picture.

![](https://github.com/ProSkills101/Stock_price_prediction/blob/main/Screenshot%202022-08-04%20155049.png)

Simply ctrl+click to go to the website. In case it does not work, though, simply type the link in any browser and you will be redirected to your website. 

You should be greeted with something like this:

![](https://github.com/ProSkills101/Stock_price_prediction/blob/main/Screenshot%202022-08-04%20155113.png)

The stock displayed will be Tesla (TSLA) by default. To view the activity of other stocks, simply input the **ticker** (not the name) of the company in the search box and press enter.

## Updates

Major update 1
* Moved to Google Colab! (Link: https://colab.research.google.com/drive/1_OB65l9KkxEuSwESgG0AIP36z7lTLIA3?hl=en#scrollTo=u3PsCF-8FaSA)

Major update 2
* Stylistic improvements along with large amounts of bug fixes.
  
## Notes

It has been discovered that the Google Colab version may be reliant on pre-existing files. Fixing is in progress. In the meantime, the code version will also be renewed frequently in order for updates to reach everyone.
  
## Future updates

* (Bugless) Incorporation of other existing prediction/visualization mechanisms
* * fbprophet
  * yfinance
* Incorporation of volume into the main chart

## References

https://github.com/JonsonChang/finance
