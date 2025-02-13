# CryptoPortfolioTracker 🪙  
Track your cryptocurrency transactions and portfolio with live price updates.

## 📌 About  
I created this project to gain experience with **Python, APIs, and GUI development**, while also using it to track my own cryptocurrency investments and trades.  

This is my **first real program built independently**, so there may be issues I haven’t encountered yet. Feel free to suggest improvements! I also plan to enhance the **visual design** and package the program into an **.exe format**.

## 🚀 Features  
✅ **Live Price Updates** using [CoinMarketCap API](https://coinmarketcap.com/api/)  
✅ **Track Portfolio Holdings** (Displays all assets + past holdings in blue)  
✅ **Automated USDC Balance Adjustment** (Tracks stablecoin balance based on transactions)  
✅ **Sortable Portfolio Table** (Sort by any column for easy analysis)  
✅ **Auto-Generated Files** (`config.json`, `portfolio.json`, `transactions.json`)  

## 📂 How It Works  
1. **First Run:**  
   - The script **creates a `config.json` file**, where you’ll need to input your **CoinMarketCap API key** (free to get).  
   - You’ll also be prompted to **initialize `portfolio.json`** with your starting USDC or stablecoin balance.  
2. **Adding Transactions:**  
   - When you log your **first trade**, a `transactions.json` file is **automatically created**.  
   - Every transaction **updates your USDC balance** accordingly.  
3. **Viewing Portfolio:**  
   - The portfolio displays **current holdings** and **past holdings (highlighted in blue)**.  
   - You can **sort holdings** by any column (e.g., price, balance, profit/loss).  

## 🛠 Setup Instructions  
1. **Clone this repository**  
   ```bash
   git clone https://github.com/yourusername/CryptoPortfolioTracker.git
   cd CryptoPortfolioTracker
   ```
2. **Install required dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the script**  
   ```bash
   python main.py
   ```
4. **Enter your API key** in config.json (`config.json` is created automatically).  
5. **Initialize your portfolio** by entering your **USDC/stablecoin balance**.  
6. **Start tracking your transactions!** 🎯  

## 🏗 Future Improvements  
- 💡 **Improve GUI visuals**  
- 🖥 **Convert to .exe for easy distribution**  
- 📊 **Add more analytics & charting tools**  

## 🤝 Contributing  
Have suggestions or found a bug? Feel free to **open an issue** or **submit a pull request**!  
