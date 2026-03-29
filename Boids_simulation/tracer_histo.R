data <- read.csv("durees.csv")

hist(
  data$duree_ms,
  breaks = 30,
  col    = "steelblue",
  border = "white",
  main   = "Distribution des temps de calcul",
  xlab   = "Temps de calcul (ms)",
  ylab   = "Nombre de frames"
)

abline(v = mean(data$duree_ms), col = "red", lwd = 2, lty = 2)
legend("topright", legend = paste("Moyenne :", round(mean(data$duree_ms), 2), "ms"),
       col = "red", lty = 2, lwd = 2)
