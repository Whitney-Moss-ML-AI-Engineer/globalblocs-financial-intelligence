# GlobalBLOCS EDA profile
# Install once: install.packages(c("readr", "dplyr", "ggplot2", "tidyr", "urca", "tseries"))
library(readr)
library(dplyr)
library(ggplot2)
library(tidyr)
library(urca)
library(tseries)

args <- commandArgs(trailingOnly = TRUE)
input_path <- if (length(args) >= 1) args[[1]] else "data/processed/panel.csv"
value_col <- if (length(args) >= 2) args[[2]] else "value"
date_col <- if (length(args) >= 3) args[[3]] else "year"
out_dir <- "artifacts/eda_r"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

df <- read_csv(input_path, show_col_types = FALSE)
write_csv(as.data.frame(summary(df)), file.path(out_dir, "summary.csv"))
missing <- tibble(variable = names(df),
                  missing_fraction = vapply(df, function(x) mean(is.na(x)), numeric(1))) %>%
  arrange(desc(missing_fraction))
write_csv(missing, file.path(out_dir, "missingness.csv"))

numeric_df <- df %>% select(where(is.numeric))
if (ncol(numeric_df) >= 2) {
  write_csv(as.data.frame(cor(numeric_df, use = "pairwise.complete.obs")),
            file.path(out_dir, "correlation.csv"))
}

if (value_col %in% names(df) && date_col %in% names(df)) {
  plot_df <- df %>%
    transmute(date = suppressWarnings(as.numeric(.data[[date_col]])),
              value = suppressWarnings(as.numeric(.data[[value_col]]))) %>%
    filter(!is.na(date), !is.na(value)) %>% arrange(date)
  if (nrow(plot_df) >= 3) {
    p <- ggplot(plot_df, aes(x = date, y = value)) +
      geom_line() + labs(title = paste(value_col, "over time"),
                         x = date_col, y = value_col) + theme_minimal()
    ggsave(file.path(out_dir, "series.png"), p, width = 10, height = 5)
    # These tests are illustrative diagnostics. Check lag choice, breaks, and
    # deterministic terms; do not interpret a single p-value mechanically.
    adf <- tryCatch(tseries::adf.test(plot_df$value), error = function(e) NULL)
    kpss <- tryCatch(tseries::kpss.test(plot_df$value), error = function(e) NULL)
    capture.output(adf, file = file.path(out_dir, "adf_test.txt"))
    capture.output(kpss, file = file.path(out_dir, "kpss_test.txt"))
  }
}
message("EDA artifacts written to ", normalizePath(out_dir))
