import React, { useState } from 'react';
import './Planner.css'
import axios from 'axios'
import ReactPlanner from './react-planner';
import myimg from '../WuSG_a.gif'


const Planner = ({ width, height, catalog, plugins, toolbarButtons, stateExtractor }) => {
    const [selectedImage, setSelectedImage] = useState(null);



    const [hide, setHide] = useState(false)
    const handleImageChange = (event) => {
        const file = event.target.files[0];
        console.log(file)
        if (file) {
            setSelectedImage(file);
        }
    };


    const handleViewARClick = () => {
        setHide(!hide)
        const formData = new FormData();
        formData.append('image', selectedImage);
        axios.post('http://localhost:5000/process_image', formData)
            .then(response => {
                // Handle the response from the backend if needed
                console.log(response.data);
            })
            .catch(error => {
                // Handle errors if any
                console.error('Error processing image:', error);
            });
    };

    return (
        <div>
            {
                !hide ? (<React.Fragment>
                    <header>
                        <h2>3D Modulation using AR for Real Estate Architecture</h2>
                    </header>

                    <div className="hero-section">
                        <div className="hero-text">
                            <h2>Explore the Future of Real Estate Architecture with 3D Modulation and Augmented Reality</h2>
                            <p>Immerse yourself in the future of architectural visualization. Our 3D modulation using augmented reality technology brings designs to life. Explore innovative solutions for real estate projects, visualize spaces like never before, and enhance your design process.</p>
                            <h4>Process</h4>
                            <p>2D Layout → 3D Model → AR View → Customization</p>
                        </div>
                        <div className="hero-image">
                            <img id="selected-image" src={selectedImage ? URL.createObjectURL(selectedImage) : myimg} alt="Selected Image" />
                        </div>
                    </div>

                    <div className="cta-buttons">
                        <input type="file" id="image-upload" placeholder='select image' onChange={handleImageChange} />
                        <button className="cta-button" onClick={handleViewARClick}>View in Augmented Reality</button>
                    </div>
                </React.Fragment>) :
                    <React.Fragment>
                        <div className='vr'>
                            <ReactPlanner width={width} height={height} catalog={catalog} plugins={plugins} toolbarButtons={toolbarButtons} stateExtractor={stateExtractor} />
                        </div>
                    </React.Fragment>
            }



        </div>
    );
};

export default Planner;
