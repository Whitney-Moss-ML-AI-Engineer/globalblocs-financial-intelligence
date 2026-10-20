# GlobalBLOCS official-source ETL starter
# Install once: install.packages(c("httr2", "jsonlite", "dplyr", "readr", "fredr", "WDI"))
# Set FRED_API_KEY in the environment; never commit API keys.
library(httr2)
library(jsonlite)
library(dplyr)
library(readr)
library(WDI)
library(fredr)

dir.create("data/raw", recursive = TRUE, showWarnings = FALSE)
dir.create("data/processed", recursive = TRUE, showWarnings = FALSE)

fetch_wdi <- function(indicator = "NY.GDP.PCAP.CD", start = 2000, end = 2024) {
  # WDI package normalizes country/year/indicator columns; retain raw and normalized copies.
  x <- WDI(country = "all", indicator = indicator, start = start, end = end,
           extra = TRUE, cache = NULL)
  x <- x %>%
    rename(value = all_of(indicator)) %>%
    mutate(source_id = "WORLD_BANK_WDI",
           indicator_id = indicator,
           retrieved_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE))
  write_csv(x, file.path("data/raw", paste0("wdi_", gsub("\\.", "_", indicator), ".csv")))
  write_csv(x, file.path("data/processed", paste0("wdi_", gsub("\\.", "_", indicator), ".csv")))
  x
}

fetch_fred <- function(series_id = "FEDFUNDS",
                       start = as.Date("2000-01-01"),
                       end = as.Date("2024-12-31")) {
  key <- Sys.getenv("FRED_API_KEY")
  if (identical(key, "")) stop("Set FRED_API_KEY in your environment.")
  fredr_set_key(key)
  x <- fredr(series_id = series_id, observation_start = start,
             observation_end = end)
  x <- x %>% mutate(source_id = "FRED", series_id = series_id,
                    retrieved_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE))
  write_csv(x, file.path("data/raw", paste0("fred_", series_id, ".csv")))
  write_csv(x, file.path("data/processed", paste0("fred_", series_id, ".csv")))
  x
}

# Example usage:
# gdp_pc <- fetch_wdi("NY.GDP.PCAP.CD", 2000, 2024)
# policy_rate <- fetch_fred("FEDFUNDS")
#
# IMF/BIS SDMX schemas vary by dataflow and version. Inspect the selected dataflow,
# dimensions, and series key before implementing a dataset-specific connector.
