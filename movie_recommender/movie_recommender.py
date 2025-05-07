'''Movie recommendation web app with Flask.'''

import pickle
import streamlit as st

# Load the assets
MODEL=pickle.load(open('movie_recommender/static/model.pkl', 'rb'))
TFIDF_MATRIX=pickle.load(open('movie_recommender/static/tfidf_matrix.pkl', 'rb'))
ENCODED_DATA_DF=pickle.load(open('movie_recommender/static/encoded_features_df.pkl', 'rb'))


def get_movie_recommendations(movie_title, model, tfidf_matrix, encoded_data_df):
    '''Takes a movie title string, looks up TFIDF feature vector for that movie
    and returns title of top 5 most similar movies'''

    # Find the query movie in the encoded data, get the index
    try:
        movie_index=encoded_data_df[encoded_data_df['title'] == movie_title].index[0]

    except IndexError:
        return 'Movie not found'

    # Get the indexes of similar movies
    _, indices=model.kneighbors(tfidf_matrix[movie_index])

    # Extract the titles of the similar movie
    similar_movies=[encoded_data_df['title'][i] for i in indices[0]]
    
    return similar_movies[1:]


if __name__ == '__main__':

    # Page title
    st.title('KNN movie recommender')

    input_movie=st.selectbox(
        label='Enter a movie title:', 
        options=ENCODED_DATA_DF['title'],
        placeholder='Star Wars'
    )

    if len(input_movie) > 0:
        recommendations=get_movie_recommendations(
            input_movie,
            MODEL,
            TFIDF_MATRIX,
            ENCODED_DATA_DF
        )

        recommendations='\n'.join(recommendations)
        st.text(recommendations)
