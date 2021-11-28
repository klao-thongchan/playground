# Box office Star Wars (in millions!)
new_hope <- c(460.998, 314.4)
empire_strikes <- c(290.475, 247.900)
return_jedi <- c(309.306, 165.8)

# Construct matrix
star_wars_matrix <- matrix(c(new_hope, empire_strikes, return_jedi), nrow = 3, byrow = TRUE)

# Vectors region and titles, used for naming
region <- c("US", "non-US")
titles <- c("A New Hope", "The Empire Strikes Back", "Return of the Jedi")

# Name the columns with region
colnames(star_wars_matrix) <- region

# Name the rows with titles
rownames(star_wars_matrix) <- titles

# Print out star_wars_matrix
star_wars_matrix

#------------------------------------
# Construct star_wars_matrix
box_office <- c(460.998, 314.4, 290.475, 247.900, 309.306, 165.8)
region <- c("US", "non-US")
titles <- c("A New Hope", 
                 "The Empire Strikes Back", 
                 "Return of the Jedi")
               
star_wars_matrix <- matrix(box_office, 
                      nrow = 3, byrow = TRUE,
                      dimnames = list(titles, region))

# Calculate worldwide box office figures
worldwide_vector <- rowSums(star_wars_matrix)

#printout
worldwide_vector

#-----------------------------------------------
# Construct star_wars_matrix
box_office <- c(460.998, 314.4, 290.475, 247.900, 309.306, 165.8)
region <- c("US", "non-US")
titles <- c("A New Hope", 
            "The Empire Strikes Back", 
            "Return of the Jedi")
               
star_wars_matrix <- matrix(box_office, 
                      nrow = 3, byrow = TRUE,
                      dimnames = list(titles, region))

# The worldwide box office figures
worldwide_vector <- rowSums(star_wars_matrix)

# Bind the new variable worldwide_vector as a column to star_wars_matrix
all_wars_matrix <- cbind(star_wars_matrix, worldwide_vector)

#print
all_wars_matrix

#--------------------------------------------
# star_wars_matrix and star_wars_matrix2 are available in your workspace
star_wars_matrix  
star_wars_matrix2 

# Combine both Star Wars trilogies in one matrix
all_wars_matrix <- rbind(star_wars_matrix, star_wars_matrix2)

#print
all_wars_matrix

#output
#                           US non-US
#A New Hope              461.0  314.4
#The Empire Strikes Back 290.5  247.9
#Return of the Jedi      309.3  165.8
#The Phantom Menace      474.5  552.5
#Attack of the Clones    310.7  338.7
#Revenge of the Sith     380.3  468.5

#--------------------------------------------------

# all_wars_matrix is available in your workspace
all_wars_matrix

# Select the non-US revenue for all movies
non_us_all <- all_wars_matrix[, 2]
#all in column2
  
# Average non-US revenue
mean(non_us_all)
  
# Select the non-US revenue for first two movies
non_us_some <- all_wars_matrix[1:2,2]
#just first and second in column2
  
# Average non-US revenue for first two movies
mean(non_us_some)

#-------------------------------------
# all_wars_matrix is available in your workspace
all_wars_matrix

# Estimate the visitors
visitors <- all_wars_matrix/5
#the ticket is 5 dollars

# Print the estimate to the console
visitors

#-----------------------------------
# all_wars_matrix and ticket_prices_matrix are available in your workspace
all_wars_matrix
ticket_prices_matrix

# Estimated number of visitors
visitors <- all_wars_matrix/ticket_prices_matrix
visitors

# US visitors
us_visitors <- visitors[,1]
us_visitors

# Average number of US visitors
mean(us_visitors)

#-----------------------------------