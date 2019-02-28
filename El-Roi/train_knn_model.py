from roi_backbone.mlearning_knn_model import train

if __name__ == "__main__":

    # Train the model from the newly captured picture
    print("Training KNN classifier...")
    classifier = train("knn_training_model/training_dataset", model_save_path="trained_member_knn_model_new.clf", n_neighbors=3)
    print("Training complete!")
