# Terroir
ter·roir (*noun*)
/terˈwär/

The complete natural environment in which a particular wine is produced, including factors such as the soil, topography, and climate.

Utilities for scraping wine data from stores, normalizing them into models, and (eventually) aggregating review data.

## Motivation

This started because of two desires:
 1. I'm a regular attendee of the Winnipeg Wine Festival. There are hundreds of wines to sample at this event, and one can only sanely consume so much wine in a few hours. In past years I'd spent days looking up wine ratings in order to create a shortlist of must-try wines. I figured there had to be a way to automate this.
 2. There's a tiny wine selection (Liquor Mart Express) at my go-to grocery store, but Liquor Marts' website provides no way to filter inventory by store. When people go to pick up a wine there for me, I have no way of telling them what I would like since it's impossible to know what is available in their tiny stock. Store information is available though, so I thought maybe there was a way to scrape it out.

## Setup

Create a Python 3.7 virtual environment (I'm using `virtualenv` but `pyenv` is preferred now).
```
virtualenv -p python3.7 env
```

Install the terroir package and dependencies:
```
python setup.py develop
```
(or `install`, for a production-style package install).

This will install the package as well as some command line entry points.

URLs and parsers are configured in the `configs/` files. Config files are looking to be overkill so far for this project, but I'm not sure how far things will go and it's not the worst thing to have set up.

## Usage

More details are available in the command help info, but at a glance:
```
terroir fetch_inventory [store]
```
`fetch_inventory` will scrape a store webpage to build up a list of product URLs. Currently supports the Liquor Mart and Kenaston Wine Mart pages.

```
terroir update_models [store]
```

`update_models` will iterative over the list of previously fetched product URLs, scrape out wine data, and write data to json files managed by python's `tinydb` module.

Run `pytest` at the project root to run project tests.

## First Attempts

I've included a `prototype_scripts/` directory which includes some one-off dirty scripts to accomplish my goals. They weren't pretty but it informs some of the approach to a version 2 implemented by the Terroir package.

#### Getting Wine Festival Data
 * I parsed a wine festival pdf guide to build up a wine list, then ran each wine against Vivino's (wine rating site) search endpoint.
* This was really problematic because the guide wine names did not match Vivino's endpoint names, and the search interface got really unreliable if the names were more than 2 or 3 words.
*  To deal with this I started shortening my names but time was running out before the festival and this turned out really inelegant (literally just lopped off words and kept trying to search). This lead to lower match confidence for a lot of wines.
* I ended up including a confidence score in my final generated report. Low confidence score meant I had to manually look up the wine rating. Generated data is in `prototype_scripts/wine_fest_vivino.csv`.
* Ultimately this showed me that using the search endpoint was not a good approach, and that I'll have to scrape Vivino data more comprehensively for a fully automated review aggregation.

#### Figuring out wines available at an LC

* This was pretty simple, just tedious and time-consuming to scrape.
* Store lists are paginated. Fortunately the one I was looking for at the time was in the first page, but Terroir's `fetch_inventory` has to be more clever to be complete.
* Ultimately managed to get wine list (`bison_wines.html`) and ran it through the rating searcher used above to get get an idea of ratings of available wines.

## Next things to work on

1. Finish the Kenaston model updater;
2. Write a Vivino scraper so I can build up a reviews database and cross-reference it (ultimately solving motivation #1, and being able to use these ratings to inform regular purchases), higher accuracy than the search endpoint implementation;
3. Add command for filtering LC results by store;
4. Support ability to search more stores.