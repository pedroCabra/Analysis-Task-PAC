library("ggplot2")
library("scales")
library("zoo")
#read data builded in python
setwd("D:/dropbox_uniandes/Dropbox/proyectosPersonales/predoc ML")
datos <- read.csv("RdataBase.csv")
#change matlab dateformat to R 
datos[,'dob_date'] <- as.Date(datos[,'dob'] - 1, origin = '0000-01-01')
#supposing that the photo was taken in the middle of the year (365.24 days per year)
datos[,'photo_date'] <- as.Date(paste0(datos[,"photoTaken"],'-06-30'))
datos[,'age'] <- as.numeric(round((datos[,'photo_date'] - datos[,'dob_date'])/365.25))
#leaving age bewtween 0 and 120 years old (the other ones are supposed to be typos)
datos <- datos[datos[,'age']>=0&datos[,'age']<=120,]

#age distribution
p <- ggplot(datos, aes(x=datos[,'age'])) +
                        geom_histogram(aes(y=..density..),colour="black", fill="white",bins=50)+
                        geom_density(alpha=.2, fill='red')+
                        #scale_y_continuous(labels = scales::percent_format())+
                        labs(title = 'Age Distribution',
                             caption = "Source: IMDB dataset",
                             y = "Density",x='Age') +
                    scale_x_continuous(limits = c(0,120),
                     breaks = seq(from=0,to=120,by=10))+
                        theme_minimal()+theme(plot.caption = element_text(hjust=0,size=10),
                                              plot.title = element_text(hjust=.5,size=25),
                                              axis.text.y=element_blank(),
                                              axis.ticks.y=element_blank(),
                                              axis.title.x = element_text(size=20),
                                              axis.title.y = element_text(size=20),
                                              axis.text.x=element_text(size=15,angle=90))
ggsave('grafica.jpg',p)

descriptivas <- round(c(mean(datos[,'age']),sd(datos[,'age']),
                        quantile(datos[,'age'],probs = c(0,.05,.1,.25,.5,.75,.9,.95,1))),2)
descriptivas[-2:-1] <- round(descriptivas[-2:-1],0)
names(descriptivas)[1:2] <- c('Mean','SD')
write.csv(t(descriptivas),'tablaDesc.csv',row.names = T)

#15-25 years old bucket
ageRange <- c(15,25)
##every obs has age data
which(is.na(datos[,'age']))
#$frecuency for each age
frecAge <- table(datos[,'age'])
##sum in the range
rangePop <- sum(frecAge[as.numeric(names(frecAge))>=ageRange[1]&as.numeric(names(frecAge))<=ageRange[2]])
rangePop
rangePop/sum(frecAge)*100


#30 years old males
##create a sub sample of only men
datosMen <- datos[datos[,"gender"]==1,]
#find 30 years frequency
frecAgeMen <- as.numeric(table(datosMen[,"age"])['30'])
frecAgeMen/sum(frecAge)
#not identified
sum(is.na(datos[,"gender"]))/sum(frecAge)*100
#some descriptive statistics
frecAge/sum(frecAge)*100
rollapply(frecAge/sum(frecAge)*100,5,sum)

table(datos[,'gender'])/nrow(datos)
table(datos[,'gender'])/sum(table(datos[,'gender']))

#save csv to read it in python
write.csv(datos,'Rresult.csv',row.names = F)
