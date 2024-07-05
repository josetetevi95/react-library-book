import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import ConfirmationPopup from './ConfirmationPopup'; // Assume this is the path

export default function UpdateScreen({ route, navigation }) {
    const { bookId } = route.params;
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [year, setYear] = useState("");
    const [author, setAuthor] = useState("");
    const [category, setCategory] = useState("");
    const [modalVisible, setModalVisible] = useState(false);

    const baseUrl = "http://127.0.0.1:7000";

    useEffect(() => {
        fetchBookDetails();
    }, [bookId]);

    const fetchBookDetails = async () => {
        try {
            const response = await fetch(`${baseUrl}/api/books/${bookId}`);
            const data = await response.json();
            if (data) {
                setTitle(data.title || "");
                setDescription(data.description || "");
                setYear(data.year ? data.year.toString() : "");
                setAuthor(data.author || "");
                setCategory(data.category || "");
            }
        } catch (error) {
            console.error('Error fetching book details:', error);
        }
    };

    const handleConfirm = async () => {
        const book = { title, description, year, author, category };
        try {
            const response = await fetch(`${baseUrl}/api/books/${bookId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(book)
            });
            if (response.ok) {
                navigation.goBack();
            }
        } catch (error) {
            console.error('Error updating book:', error);
        }
        setModalVisible(false);
    };

    return (
        <View style={styles.container}>
            <Text>Update Book</Text>
            <TextInput
                style={styles.input}
                value={title}
                onChangeText={setTitle}
                placeholder="Title" />
            <TextInput
                style={styles.input}
                value={description}
                onChangeText={setDescription}
                placeholder="Description"
                multiline />
            <TextInput
                style={styles.input}
                value={year}
                onChangeText={setYear}
                placeholder="Year"
                keyboardType="numeric" />
            <TextInput
                style={styles.input}
                value={author}
                onChangeText={setAuthor}
                placeholder="Author" />
            <TextInput
                style={styles.input}
                value={category}
                onChangeText={setCategory}
                placeholder="Category" />
            <Button title="Update Book" onPress={() => setModalVisible(true)} />
            <ConfirmationPopup
                visible={modalVisible}
                onClose={() => setModalVisible(false)}
                onConfirm={handleConfirm}
                title="Confirm Update"
                message="Are you sure you want to update this book?"
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#fff',
    },
    input: {
        height: 40,
        borderColor: 'gray',
        borderWidth: 1,
        marginBottom: 10,
    }
});
