### Getting Started

```bash
# Clone or download this project
cd your-project-folder

# Install the required packages
pip install -r requirements.txt

# Set up the database
python manage.py makemigrations
python manage.py migrate

# Create an admin user
python manage.py createsuperuser

# Load Indian dummy data (products in INR, Indian brands, etc.)
python manage.py populate_indian_data

# Run the server
python manage.py runserver
```

That's it! Visit `http://localhost:8000` and you should see the shop.

### Admin Access

- Go to `/admin/`
- Login with your superuser account
- Add some products and categories to get started

### Machine Learning Models

The recommendation system uses three different approaches:

1. **Collaborative Filtering** - "People who bought X also bought Y"
2. **Content-Based Filtering** - "You liked phones, here are more phones"
3. **Hybrid Approach** - Combines both methods for better results

The AI learns from user interactions like:

- What products they view
- What they like/dislike (thumbs up/down)
- What they add to cart
- What they actually buy

### How It Works

- Users interact with products (view, like, purchase)
- The system tracks these interactions
- ML algorithms analyze the data
- Recommendations get generated in real-time
- The more data, the better the suggestions

### Training the Models

The AI models retrain automatically when there's enough new data. You can also manually retrain them through the admin API if needed.

## Cython Optimization

Some parts of the recommendation engine are written in Cython for speed:

- **Similarity calculations** - fast cosine similarity
- **Matrix operations** - Optimized for large datasets
- **Recommendation scoring** - fast product ranking

### Fallback

Don't worry if Cython doesn't compile on your system - the code automatically falls back to pure Python implementations. You'll still get all the features, just a bit slower.

## File Structure

```
├── shop/                   # Main e-commerce app
├── recommendations/        # AI recommendation engine
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── requirements.txt      # Python packages
└── manage.py            # Django management
```

## Tech Stack

- **Backend**: Django, Python
- **AI/ML**: scikit-learn, pandas, numpy
- **Performance**: Cython optimization
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Database**: SQLite
