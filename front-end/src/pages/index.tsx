import Head from 'next/head'
import { Inter } from 'next/font/google'
import HomeInterface from './HomeInterface'
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.min.css';

const inter = Inter({ subsets: ['latin'] })

export default function Home() {
  return (
    <>
      <Head>
        <title>YT Media Downloader</title>
        <meta name="description" content="Download de vídeos e áudio do youtube pela URL" />
        <meta name="description" lang="en" content="Download youtube videos and audio by URL" />
        <meta name="keywords" content="download, vídeos, áudio, youtube, URL" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <HomeInterface />
        <ToastContainer />
      </main>
    </>
  )
}
