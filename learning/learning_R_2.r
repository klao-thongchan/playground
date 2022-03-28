# Code to build factor_survey_vector
survey_vector <- c("M", "F", "F", "M", "M")
factor_survey_vector <- factor(survey_vector)

# Specify the levels of factor_survey_vector
levels(factor_survey_vector) <- c("Female", "Male")

factor_survey_vector

#---------------------------------------------
# Build factor_survey_vector with clean levels
survey_vector <- c("M", "F", "F", "M", "M")
factor_survey_vector <- factor(survey_vector)
levels(factor_survey_vector) <- c("Female", "Male")
factor_survey_vector

# Generate summary for survey_vector
summary(survey_vector)

# Generate summary for factor_survey_vector
summary(factor_survey_vector)

# Result
#Female   Male 
#     2      3 
#--------------------------------------------------
install.packages(c("askpass", "backports", "BH", "bit", "bit64", "bitops", "blob", "caTools", "cli", "clipr", "config", "crayon", "curl", "DBI", "dbplyr", "digest", "dplyr", "ellipsis", "evaluate", "fansi", "forcats", "generics", "glue", "haven", "highr", "hms", "htmltools", "htmlwidgets", "httpuv", "httr", "jsonlite", "knitr", "later", "magrittr", "markdown", "mime", "mongolite", "odbc", "openssl", "packrat", "pillar", "pkgconfig", "PKI", "prettyunits", "profvis", "progress", "promises", "purrr", "r2d3", "R6", "rappdirs", "Rcpp", "RCurl", "readr", "rJava", "RJDBC", "RJSONIO", "rlang", "rmarkdown", "rprojroot", "rsconnect", "rstudioapi", "shiny", "sparklyr", "stringi", "sys", "tibble", "tidyr", "tidyselect", "tinytex", "utf8", "withr", "xfun", "xml2", "yaml"))
#-----------------------------------------
# Definition of vectors
name <- c("Mercury", "Venus", "Earth", 
          "Mars", "Jupiter", "Saturn", 
          "Uranus", "Neptune")
type <- c("Terrestrial planet", 
          "Terrestrial planet", 
          "Terrestrial planet", 
          "Terrestrial planet", "Gas giant", 
          "Gas giant", "Gas giant", "Gas giant")
diameter <- c(0.382, 0.949, 1, 0.532, 
              11.209, 9.449, 4.007, 3.883)
rotation <- c(58.64, -243.02, 1, 1.03, 
              0.41, 0.43, -0.72, 0.67)
rings <- c(FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, TRUE)

# Create a data frame from the vectors
planets_df <- data.frame(name,type,diameter,rotation,rings)
planets_df
#-----------------------------------------------------------
# Play around with the order function in the console
a <- c("Klao", "Yam", "Arkin")
order(a)
#[1] 3 1 2

a[order(a)]
#[1] "Arkin" "Klao"  "Yam"  
#---------------------------------------------------------
# planets_df is pre-loaded in your workspace
planets_df

# Use order() to create positions
positions <- order(planets_df$diameter)
positions

# Use positions to sort planets_df
planets_df[positions,]

#---------------------------------------------------