# ==========================================================
# File Name:
# embeddings.py
#
# Purpose:
# ----------------------------------------------------------
# Creates embedding model for RAG.
#
# Text documents are converted into vectors.
#
# Used by:
# vector_store.py
#
# ==========================================================


# LangChain community HuggingFace embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings




# ==========================================================
# Function:
# get_embeddings()
#
# Returns embedding model
#
# ==========================================================


def get_embeddings():


    # ------------------------------------------------------
    # Load Sentence Transformer model
    #
    # Model:
    # all-MiniLM-L6-v2
    #
    # It converts text into numerical vectors.
    #
    # ------------------------------------------------------


    embeddings = HuggingFaceEmbeddings(


        model_name=
        "sentence-transformers/all-MiniLM-L6-v2",



        # Run model on CPU

        model_kwargs={

            "device": "cpu"

        },



        # Normalize vectors
        # improves similarity search

        encode_kwargs={

            "normalize_embeddings": True

        }

    )



    return embeddings