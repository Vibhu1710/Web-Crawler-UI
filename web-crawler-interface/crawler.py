import crawler_scripts.Leads.Luminous as Luminous
import crawler_scripts.Leads.Crabtree as Crabtree
import crawler_scripts.Leads.Godrej as Godrej
import crawler_scripts.Leads.Malabar as Malabar
import crawler_scripts.Leads.Usha as Usha

import crawler_scripts.Competition.Mahindra as Mahindra
import crawler_scripts.Competition.Hyundai as Hyundai
import crawler_scripts.Competition.Isuzu as Isuzu

import crawler_scripts.Fssai_data.Fssai as Fssai


website_map_dict = globals()

def scrape(websiteId, skip = -100):
    website_map_dict[websiteId].run(websiteId, skip)
